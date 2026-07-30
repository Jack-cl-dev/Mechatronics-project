from microbit import *
import utime
import time
import compass

c = compass.Compass()

while True:
    print(c.upright_heading())
    sleep(1000)