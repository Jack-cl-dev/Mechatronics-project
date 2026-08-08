from maqueen import Maqueen
from microbit import *
robot = Maqueen()

while True:
    left = robot.line_left()
    right = robot.line_right()

    robot.led_left(left)
    robot.led_right(right)