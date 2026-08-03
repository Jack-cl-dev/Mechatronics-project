from microbit import *
import utime
import audio

class ObstacleDetector:
    def __init__(self, robot, stop_distance=10):
        self.robot = robot
        self.stop_distance = stop_distance
        self.horn_duration = 2000
        self.horn_active = False
        self.close_streak = 0
        self.confirm_needed = 3   # readings in a row before we trust it

    def check(self):
        distance = self.robot.ultrasound_measure()

        if distance <= 0 or distance > self.stop_distance:
            self.close_streak = 0
            return False

        self.close_streak += 1
        return self.close_streak >= self.confirm_needed

    def react(self):
        self.horn_active = True
        self.robot.motor_left(0, 0)
        self.robot.motor_right(0, 0)
        audio.play(Sound.SAD)
        utime.sleep_ms(self.horn_duration)
        self.horn_active = False
        self.close_streak = 0
