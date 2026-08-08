from maqueen import Maqueen
from microbit import *
import utime
import random

robot = Maqueen()

utime.sleep_ms(1000)

for x in range(256):
    robot.rgb_front_left(0,0,x)
    robot.rgb_rear_left(0,0,x)
    robot.rgb_front_right(0,0,x)
    robot.rgb_rear_right(0,0,x)

utime.sleep_ms(1000)

for x in range(100):
    red = random.randint(0,255)
    green = random.randint(0,255)
    blue = random.randint(0,255)
    robot.rgb_front_left(red,green,blue)
    robot.rgb_rear_left(red,green,blue)
    robot.rgb_front_right(red,green,blue)
    robot.rgb_rear_right(red,green,blue)
    utime.sleep_ms(100)

robot.rgb_front_left(0,0,0)
robot.rgb_rear_left(0,0,0)
robot.rgb_front_right(0,0,0)
robot.rgb_rear_right(0,0,0)