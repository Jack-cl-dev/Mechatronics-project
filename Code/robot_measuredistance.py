from maqueen import Maqueen
from microbit import *
import utime

robot = Maqueen()

v0 = Image(
    "00000:"
    "00000:"
    "00900:"
    "00000:"
    "00000")

v1 = Image(
    "00000:"
    "00900:"
    "09090:"
    "00900:"
    "00000")

v2 = Image(
    "09990:"
    "90009:"
    "90009:"
    "90009:"
    "09990")


values = [v0, v1, v2]

while True:
    distance_in_cm = robot.ultrasound_measure()
    delay_in_ms = int(10 * distance_in_cm)
    for v in values:
        display.show(v)
        utime.sleep_ms(delay_in_ms)
