from microbit import *
import utime

class Headlights:
    def __init__(self, robot, on_threshold=60, off_threshold=90, check_every_ms=250):
        self.robot = robot
        self.on_threshold = on_threshold    # below this = "dark", turn ON
        self.off_threshold = off_threshold  # above this = "bright", turn OFF
        self.check_every_ms = check_every_ms
        self.on = False
        self.last_check = utime.ticks_ms()

    def update(self):
        now = utime.ticks_ms()
        if utime.ticks_diff(now, self.last_check) < self.check_every_ms:
            return self.on
        self.last_check = now

        level = display.read_light_level()  # 0 (dark) .. 255 (bright)

        if self.on and level > self.off_threshold:
            self.on = False
            self.robot.led_left(0)
            self.robot.led_right(0)
        elif not self.on and level < self.on_threshold:
            self.on = True
            self.robot.led_left(1)
            self.robot.led_right(1)

        return self.on
