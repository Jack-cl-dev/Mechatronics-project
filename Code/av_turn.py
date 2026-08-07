import utime
from logger import log

TURN_SPEED = 70
FWD = 0
BWD = 1
BURST_MS = 60
SETTLE_MS = 40
TURN_TIMEOUT_MS = 3000
FLIP_CHECK_BURSTS = 4
TIMED_TURN_MS_PER_90 = 700
HEADING_TOL_DEG = 12
POLL_MS = 20

def _heading(self):
    if not self.use_compass:
        return None
    h = self.compass.upright_heading()
    log.log("heading", h)
    return h

class TurnMixin:
    """Closed-loop (compass) and open-loop (timed) pivoting.

    Host class must provide: self.robot, self.compass, self.use_compass,
    self.turn_sign, self._flipped, self._log(), self._stop().
    """

    def _spin(self, sign):
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

    def _timed_turn(self, delta):
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
        """Pivot until pointing at `target` degrees. True if the compass got
        us there, False if we had to fall back to a timed turn."""
        current = self._heading()
        if current is None:
            self._timed_turn(fallback_delta)
            return False
        elif (not self._flipped
              and bursts >= FLIP_CHECK_BURSTS
              and abs(error) >= start_abs_error):
            self.turn_sign = -self.turn_sign
            self._flipped = True
            log.log("flip", "err={:.1f} start_err={:.1f}".format(abs(error), start_abs_error))
            self._log("no progress, flipping turn sense")

        start = utime.ticks_ms()
        start_abs_error = None
        bursts = 0
        while utime.ticks_diff(utime.ticks_ms(), start) < TURN_TIMEOUT_MS:
            error = self.compass.heading_error(target, current)
            if abs(error) <= HEADING_TOL_DEG:
                self._stop()
                return True

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
