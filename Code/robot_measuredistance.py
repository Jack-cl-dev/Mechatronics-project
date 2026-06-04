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
