from microbit import *
import utime
from compass import Compass

# Motor direction bits, same convention as main.py / Maqueen.
FWD = 0
BWD = 1

TURN_SPEED   = 70      # wheel speed while pivoting in place
CLEAR_SPEED  = 80      # wheel speed while driving past the obstacle

SIDESTEP_DEG    = 90   # how far off course to turn to go around
HEADING_TOL_DEG = 12   # close enough to the target heading to stop turning

# Turns are pulsed rather than continuous: the motors are electromagnets and
# swamp the magnetometer while they're drawing current, so we spin a little,
# stop, let the field settle, then read the heading.
BURST_MS  = 60
SETTLE_MS = 40

TURN_TIMEOUT_MS = 3000   # give up on closed-loop turning after this

# How many bursts to spin before deciding we're turning the wrong way. One
# burst only moves us a few degrees, so comparing consecutive readings can't
# tell a wrong-way turn from magnetometer noise -- this compares against where
# the turn started instead.
FLIP_CHECK_BURSTS = 4

# Open-loop fallback, used only when the compass is uncalibrated or a
# closed-loop turn times out. MEASURE THIS ON THE ROBOT: time a 90-degree
# pivot at TURN_SPEED on the surface you're testing on and put the result here.
TIMED_TURN_MS_PER_90 = 700

# One sidestep increment. Kept short on purpose -- the decision to stop
# sidestepping comes from the ultrasound, not from a total travel time, so this
# is just how far we shuffle between checks.
STEP_DRIVE_MS = 350

REJOIN_DRIVE_MS = 2000   # forward run once the course is confirmed clear

# --- failsafe ---
MAX_SIDESTEPS        = 8      # stop shuffling sideways after these many steps
# Ceiling on the whole manoeuvre. Checked once per sidestep, so the real worst
# case is this plus the final turn back onto course (up to TURN_TIMEOUT_MS).
MANOEUVRE_TIMEOUT_MS = 20000

SIDE_CLEAR_CM = 25       # a direction counts as open if nothing is this close
PROBE_SAMPLES = 3        # ultrasound readings folded into one decision
POLL_MS       = 20


class ObjectAvoidance:
    """Drives around an obstacle the ObstacleDetector has stopped in front of.

    The manoeuvre is closed-loop on both sensors rather than a timed routine:

      1. Pivot 90 degrees toward whichever side the ultrasound says is open.
      2. Shuffle forward one short step.
      3. Pivot back onto the original heading and probe. Still blocked? Go
         back to 2. Clear? The obstacle is behind us, so drive on.

    So "am I past it yet" is answered by the distance sensor each time round,
    not by assuming a fixed travel distance. Every stage is still bounded --
    MAX_SIDESTEPS, MANOEUVRE_TIMEOUT_MS, and TURN_TIMEOUT_MS mean it always
    returns rather than shuffling forever.

    It deliberately does NOT try to re-acquire the line itself; main.py's
    lost-line search already does that, so this hands back as soon as it's past.

    Line_seen -- optional callable returning True when a line sensor is over
                 the line. main.py owns the sensor polarity, so it passes its
                 own helper in rather than this class guessing.
    """

    def __init__(self, robot, stop_distance=10, line_seen=None, verbose=True):
        self.robot = robot
        self.stop_distance = stop_distance
        self.line_seen = line_seen
        self.verbose = verbose
        self.compass = Compass()
        # +1 means "the clockwise motor pattern really does turn us clockwise".
        # If the magnetometer axes are mirrored on this build, the first turn
        # detects it and flips this once, for the rest of the run.
        self.turn_sign = 1
        self.use_compass = False
        self._flipped = False
        self._deadline = 0
        self.last_result = None

    # --- low level ---------------------------------------------------------

    def _log(self, message):
        if self.verbose:
            print("[avoid] " + message)

    def _stop(self):
        self.robot.motor_left(0, 0)
        self.robot.motor_right(0, 0)

    def _out_of_time(self):
        return utime.ticks_diff(self._deadline, utime.ticks_ms()) <= 0

    def _spin(self, sign):
        """Start pivoting in place. Sign >= 0 turns clockwise (to the right)."""
        if sign >= 0:
            self.robot.motor_left(TURN_SPEED, FWD)
            self.robot.motor_right(TURN_SPEED, BWD)
        else:
            self.robot.motor_left(TURN_SPEED, BWD)
            self.robot.motor_right(TURN_SPEED, FWD)

    def _burst(self, sign):
        self._spin(sign)
        utime.sleep_ms(BURST_MS)
        self._stop()
        utime.sleep_ms(SETTLE_MS)

    def _heading(self):
        if not self.use_compass:
            return None
        return self.compass.upright_heading()

    def _probe(self):
        """Nearest valid distance in cm, or -1 if nothing echoed back."""
        nearest = -1
        for _ in range(PROBE_SAMPLES):
            distance = self.robot.ultrasound_measure()
            if distance > 0 and (nearest < 0 or distance < nearest):
                nearest = distance
            utime.sleep_ms(POLL_MS)
        return nearest

    @staticmethod
    def _is_clear(distance):
        # A negative reading is the sensor timing out, which means no echo came
        # back at all -- open space, not an obstacle.
        return distance < 0 or distance >= SIDE_CLEAR_CM

    # --- turning ----------------------------------------------------------

    def _timed_turn(self, delta):
        """Open-loop pivot of roughly `delta` degrees. No feedback at all."""
        if not delta:
            return
        duration = int(abs(delta) * TIMED_TURN_MS_PER_90 / 90)
        self._log("timed turn {} deg ({} ms)".format(int(delta), duration))
        self._spin(self.turn_sign if delta > 0 else -self.turn_sign)
        start = utime.ticks_ms()
        while utime.ticks_diff(utime.ticks_ms(), start) < duration:
            utime.sleep_ms(POLL_MS)
        self._stop()

    def _turn_absolute(self, target, fallback_delta):
        """Pivot until pointing at `target` degrees. True if the compass got us
        there, False if we had to fall back to a timed turn."""
        current = self._heading()
        if current is None:
            self._timed_turn(fallback_delta)
            return False

        start = utime.ticks_ms()
        start_abs_error = None
        bursts = 0
        while utime.ticks_diff(utime.ticks_ms(), start) < TURN_TIMEOUT_MS:
            error = self.compass.heading_error(target, current)
            if abs(error) <= HEADING_TOL_DEG:
                self._stop()
                return True

            # Several bursts of turning and no closer to the target means our
            # idea of "clockwise" is backwards -- either the magnetometer axes
            # are mirrored on this build or the motors are wired swapped.
            # Without this the closed loop still converges, but by turning the
            # long way round (up to 270 degrees instead of 90).
            if start_abs_error is None:
                start_abs_error = abs(error)
            elif (not self._flipped
                    and bursts >= FLIP_CHECK_BURSTS
                    and abs(error) >= start_abs_error):
                self.turn_sign = -self.turn_sign
                self._flipped = True
                self._log("no progress, flipping turn sense")
                start_abs_error = abs(error)
                bursts = 0

            self._burst(self.turn_sign if error > 0 else -self.turn_sign)
            bursts += 1
            current = self._heading()
            if current is None:
                self._timed_turn(fallback_delta)
                return False

        self._stop()
        remaining = self.compass.heading_error(target, current)
        self._log("closed-loop turn timed out, {} deg short".format(int(remaining)))
        self._timed_turn(remaining)
        return False

    def _turn_relative(self, delta):
        current = self._heading()
        if current is None:
            self._timed_turn(delta)
            return False
        return self._turn_absolute((current + delta) % 360, delta)

    def _turn_onto(self, target, fallback_delta):
        """Turn to an absolute heading, or a relative timed turn without a compass."""
        if target is None:
            self._timed_turn(fallback_delta)
            return False
        return self._turn_absolute(target, fallback_delta)

    # --- driving ----------------------------------------------------------

    def _drive_forward(self, duration_ms, stop_on_line=False):
        """Drive straight for up to duration_ms.

        Returns "blocked" if something got too close, "line" if a line sensor
        found the line, "done" if the full time elapsed.
        """
        self.robot.motor_left(CLEAR_SPEED, FWD)
        self.robot.motor_right(CLEAR_SPEED, FWD)
        start = utime.ticks_ms()
        while utime.ticks_diff(utime.ticks_ms(), start) < duration_ms:
            distance = self.robot.ultrasound_measure()
            if 0 < distance <= self.stop_distance:
                self._stop()
                return "blocked"
            if stop_on_line and self.line_seen is not None and self.line_seen():
                self._stop()
                return "line"
            utime.sleep_ms(POLL_MS)
        self._stop()
        return "done"

    # --- the manoeuvre ----------------------------------------------------

    def _choose_side(self):
        """Pivot to face the open side. Returns +1 (right), -1 (left) or None."""
        self._turn_relative(SIDESTEP_DEG)
        if self._is_clear(self._probe()):
            return 1
        self._turn_relative(-2 * SIDESTEP_DEG)
        if self._is_clear(self._probe()):
            return -1
        return None

    def avoid_obstacle(self):
        """Go around whatever is in front of us. Blocking, but bounded.

        Returns one of:
          "line" -- found the line again on the way past
          "clear" -- confirmed past an obstacle, back on the original heading
          "reversed" -- boxed in on three sides, turned around instead
          "stuck" -- ran out of sidesteps or time; back on the original
                        heading but the course was never confirmed clear
        """
        self._log("avoiding obstacle")
        self._stop()
        self._flipped = False
        self._deadline = utime.ticks_add(utime.ticks_ms(), MANOEUVRE_TIMEOUT_MS)

        # Re-check every time: main.py calibrates at boot, and this object is
        # usually constructed before that has happened.
        self.use_compass = self.compass.is_ready()
        if not self.use_compass:
            self._log("compass not calibrated, using timed turns")

        course = self._heading()          # heading to get back onto afterwards
        side = self._choose_side()

        if side is None:
            # Blocked ahead, right and left. We're at -90, of course; turn the
            # same way again to face back where we came from and retreat.
            self._log("boxed in, backing out")
            self._turn_relative(-SIDESTEP_DEG)
            self._drive_forward(REJOIN_DRIVE_MS, stop_on_line=True)
            self._stop()
            self.last_result = "reversed"
            return self.last_result

        self._log("detour to the " + ("right" if side > 0 else "left"))
        detour = side * SIDESTEP_DEG
        detour_heading = None if course is None else (course + detour) % 360

        steps = 0
        while steps < MAX_SIDESTEPS and not self._out_of_time():
            outcome = self._drive_forward(STEP_DRIVE_MS, stop_on_line=True)
            if outcome == "line":
                self._stop()
                self.last_result = "line"
                self._log("done: line")
                return self.last_result
            if outcome == "blocked":
                # The way round just closed off too -- stop shuffling.
                self._log("sidestep blocked after {} step(s)".format(steps))
                break
            steps += 1

            # Look down the original course: are we past the obstacle yet?
            self._turn_onto(course, -detour)
            if self._is_clear(self._probe()):
                self._log("course clear after {} sidestep(s)".format(steps))
                outcome = self._drive_forward(REJOIN_DRIVE_MS, stop_on_line=True)
                self._stop()
                self.last_result = "line" if outcome == "line" else "clear"
                self._log("done: " + self.last_result)
                return self.last_result

            # Still blocked, so shuffle further along and check again.
            self._turn_onto(detour_heading, detour)

        # Failsafe exit: point back along the original course and hand back, so
        # main.py's lost-line search takes over from a sane orientation.
        self._log("giving up after {} sidestep(s)".format(steps))
        self._turn_onto(course, -detour)
        self._stop()
        self.last_result = "stuck"
        return self.last_result
