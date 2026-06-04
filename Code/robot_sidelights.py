# MIT License

# Copyright (c) 2021 Kristoffer Holm

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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