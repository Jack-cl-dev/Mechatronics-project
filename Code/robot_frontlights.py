from maqueen import Maqueen
from microbit import *
import utime
robot = Maqueen()
for x in range(3):
    utime.sleep_ms(1000)
    robot.led_left(1)
    robot.led_right(1)
    utime.sleep_ms(1000)
    robot.led_left(0)
    robot.led_right(0)
