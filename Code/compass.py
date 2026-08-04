from microbit import *
import math

class Compass:
    def upright_heading(self):
        mx = compass.get_x()
        mz = compass.get_z()
        heading = math.degrees(math.atan2(mx, mz))  # mirrors compass.heading()'s atan2(x, y)
        return heading + 360 if heading < 0 else heading

    def is_ready(self):
        return compass.is_calibrated()

    def ensure_calibrated(self):
        """Run the tilt-to-fill calibration game now, if it hasn't been done.

        get_x()/get_z() return raw values without complaining when the compass
        is uncalibrated, so upright_heading() would silently drift by a large
        hard-iron offset. Calling this once at boot keeps the interactive
        calibration out of the middle of a driving manoeuvre.

        Lift the robot off the chassis and hold the micro:bit away from the
        motors while calibrating -- they are magnets and will skew the result.
        """
        if compass.is_calibrated():
            return True
        display.scroll("TILT")
        compass.calibrate()
        return compass.is_calibrated()

    def heading_error(self, target, current):
        """Signed shortest turn from `current` to `target`, in (-180, 180].

        Positive means the target is clockwise of where we're pointing.
        """
        error = (target - current) % 360
        if error > 180:
            error -= 360
        return error
