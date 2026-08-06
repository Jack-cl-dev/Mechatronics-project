import utime

CLEAR_SPEED = 80
FWD = 0
SIDE_CLEAR_CM = 25
PROBE_SAMPLES = 3
POLL_MS = 20


class DriveMixin:
    """Ultrasound probing and forward driving.

    Host class must provide: self.robot, self.stop_distance, self.line_seen,
    self._stop().
    """

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
        # A negative reading is the sensor timing out -- open space, not an
        # obstacle.
        return distance < 0 or distance >= SIDE_CLEAR_CM

    def _drive_forward(self, duration_ms, stop_on_line=False):
        """Drive straight for up to duration_ms.

        Returns "blocked" if something got too close, "line" if a line
        sensor found the line, "done" if the full time elapsed.
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
