from microbit import *
import utime
class ObjectAvoidance:
    def avoid_obstacle(self):
        print("Avoiding obstacle")
        degrees = input.compass_heading()
        while True:
            degrees = input.compass_heading()