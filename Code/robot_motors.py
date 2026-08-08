from maqueen import Maqueen
from microbit import *
import utime

robot = Maqueen()

robot.motor_left(30)
robot.motor_right(30)

utime.sleep_ms(2000)

robot.motor_left(30)
robot.motor_right(30, 1)

utime.sleep_ms(2000)

robot.motor_left(30, 1)
robot.motor_right(30, 1)

utime.sleep_ms(2000)

robot.motor_left()
robot.motor_right()