from microbit import *
import utime
import audio

class ObstacleDetector:
    def __init__(self, robot, stop_distance=10):
        self.robot = robot
        self.stop_distance = stop_distance
        self.horn_duration = 2000
        self.horn_active = False

    def check(self):
        distance = self.robot.ultrasound_measure()

        if distance <= 0:
            return False

        return distance <= self.stop_distance

    def react(self):
        self.horn_active = True

        self.robot.motor_left(0, 0)
        self.robot.motor_right(0, 0)

        audio.play(audio.Sound.SAD)
        utime.sleep_ms(self.horn_duration)

        self.horn_active = False
