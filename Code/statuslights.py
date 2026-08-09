from microbit import *
import utime
OFF     = (0, 0, 0)
GREEN   = (0, 255, 0)
BLUE    = (0, 60, 255)
AMBER   = (255, 120, 0)
RED     = (255, 0, 0)
WHITE   = (255, 255, 255)
class StatusLights:
    def __init__(self, robot):
        self.robot = robot
        self.last_update_ms = utime.ticks_ms()
        self.pulse_phase = 0
        self.flash_until = 0
    def _set_all(self, color):
        r, g, b = color
        self.robot.rgb_front_left(r, g, b)
        self.robot.rgb_rear_left(r, g, b)
        self.robot.rgb_rear_right(r, g, b)
        self.robot.rgb_front_right(r, g, b)
    def _set_left(self, color):
        r, g, b = color
        self.robot.rgb_front_left(r, g, b)
        self.robot.rgb_rear_left(r, g, b)
    def _set_right(self, color):
        r, g, b = color
        self.robot.rgb_front_right(r, g, b)
        self.robot.rgb_rear_right(r, g, b)
    def flash_clap(self):
        self.flash_until = utime.ticks_ms() + 150
    def update(self, wheels_on, obstacle_active, turning=None):
        now = utime.ticks_ms()
        if utime.ticks_diff(self.flash_until, now) > 0:
            self._set_all(WHITE)
            return
        if obstacle_active:
            self._set_all(RED)
            return
        if not wheels_on:
            self.pulse_phase = (self.pulse_phase + 1) % 40
            brightness = abs(20 - self.pulse_phase) * 12
            self._set_all((0, brightness, 0))
            return
        if turning == "left":
            self._set_left(AMBER)
            self._set_right(OFF)
        elif turning == "right":
            self._set_right(AMBER)
            self._set_left(OFF)
        else:
            self._set_all(BLUE)
