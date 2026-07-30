from microbit import *
import math

class Compass:
    def upright_heading(self):
        mx = compass.get_x()
        mz = compass.get_z()
        heading = math.degrees(math.atan2(mx, mz))  # mirrors compass.heading()'s atan2(x, y)
        return heading + 360 if heading < 0 else heading
