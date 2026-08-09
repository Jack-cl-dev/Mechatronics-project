import utime
TURN_SPEED = 70
FWD = 0
BWD = 1
MS_PER_90 = 350
POLL_MS = 20
class TurnMixin:
    def _spin(self, sign):
        if sign >= 0:
            self.robot.motor_left(TURN_SPEED, FWD)
            self.robot.motor_right(TURN_SPEED, BWD)
        else:
            self.robot.motor_left(TURN_SPEED, BWD)
            self.robot.motor_right(TURN_SPEED, FWD)
    def _turn(self, degrees):
        if not degrees:
            return
        duration = int(abs(degrees) * MS_PER_90 / 90)
        sign = 1 if degrees > 0 else -1
        self._log("timed turn {} deg ({} ms)".format(int(degrees), duration))
        self._spin(sign)
        start = utime.ticks_ms()
        while utime.ticks_diff(utime.ticks_ms(), start) < duration:
            utime.sleep_ms(POLL_MS)
        self._stop()