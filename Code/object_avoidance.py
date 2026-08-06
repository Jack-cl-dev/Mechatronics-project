from microbit import *
import utime
from compass import Compass
from av_turn import TurnMixin
from av_drive import DriveMixin

SIDESTEP_DEG = 90       # how far off course to turn to go around
STEP_DRIVE_MS = 350     # one sidestep increment
REJOIN_DRIVE_MS = 2000  # forward run once the course is confirmed clear

MAX_SIDESTEPS = 8               # stop shuffling sideways after these many steps
MANOEUVRE_TIMEOUT_MS = 20000    # ceiling on the whole manoeuvre


class ObjectAvoidance(TurnMixin, DriveMixin):
    """Drives around an obstacle the ObstacleDetector has stopped in front of.

    Closed-loop on both sensors, not a timed routine:
      1. Pivot 90 degrees toward whichever side the ultrasound says is open.
      2. Shuffle forward one short step.
      3. Pivot back onto the original heading and probe. Still blocked? Go
         back to 2. Clear? The obstacle is behind us, so drive on.

    Bounded by MAX_SIDESTEPS, MANOEUVRE_TIMEOUT_MS and TURN_TIMEOUT_MS (in
    av_turn.py) so it always returns.

    Does NOT try to re-acquire the line itself -- main.py's lost-line search
    already does that.

    line_seen -- optional callable returning True when a line sensor is over
                 the line. main.py owns the sensor polarity.
    """

    def __init__(self, robot, stop_distance=10, line_seen=None, verbose=True):
        self.robot = robot
        self.stop_distance = stop_distance
        self.line_seen = line_seen
        self.verbose = verbose
        self.compass = Compass()
        # +1 means "the clockwise motor pattern really does turn us clockwise".
        self.turn_sign = 1
        self.use_compass = False
        self._flipped = False
        self._deadline = 0
        self.last_result = None

    def _log(self, message):
        if self.verbose:
            print("[avoid] " + message)

    def _stop(self):
        self.robot.motor_left(0, 0)
        self.robot.motor_right(0, 0)

    def _out_of_time(self):
        return utime.ticks_diff(self._deadline, utime.ticks_ms()) <= 0

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

        Returns "line", "clear", "reversed" or "stuck".
        """
        self._log("avoiding obstacle")
        self._stop()
        self._flipped = False
        self._deadline = utime.ticks_add(utime.ticks_ms(), MANOEUVRE_TIMEOUT_MS)

        self.use_compass = self.compass.is_ready()
        if not self.use_compass:
            self._log("compass not calibrated, using timed turns")

        course = self._heading()
        side = self._choose_side()

        if side is None:
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
                self._log("sidestep blocked after {} step(s)".format(steps))
                break
            steps += 1

            self._turn_onto(course, -detour)
            if self._is_clear(self._probe()):
                self._log("course clear after {} sidestep(s)".format(steps))
                outcome = self._drive_forward(REJOIN_DRIVE_MS, stop_on_line=True)
                self._stop()
                self.last_result = "line" if outcome == "line" else "clear"
                self._log("done: " + self.last_result)
                return self.last_result

            self._turn_onto(detour_heading, detour)

        self._log("giving up after {} sidestep(s)".format(steps))
        self._turn_onto(course, -detour)
        self._stop()
        self.last_result = "stuck"
        return self.last_result
