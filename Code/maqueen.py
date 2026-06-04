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

from microbit import *
import neopixel
import utime

class Maqueen:

    def __init__(self):
        i2c.init()
        self.np = neopixel.NeoPixel(pin15, 4)
        pin1.write_digital(0)

    # value: {0,1}
    def led_left(self, value):
        pin8.write_digital(value)

    # value: {0,1}
    def led_right(self, value):
        pin12.write_digital(value)

    # red: {0-255}
    # green: {0-255}
    # blue: {0-255}
    def rgb_front_left(self, red, green, blue):
        self.np[0] = (red, green, blue)
        self.np.show()

    # red: {0-255}
    # green: {0-255}
    # blue: {0-255}
    def rgb_rear_left(self, red, green, blue):
        self.np[1] = (red, green, blue)
        self.np.show()

    # red: {0-255}
    # green: {0-255}
    # blue: {0-255}
    def rgb_rear_right(self, red, green, blue):
        self.np[2] = (red, green, blue)
        self.np.show()

    # red: {0-255}
    # green: {0-255}
    # blue: {0-255}
    def rgb_front_right(self, red, green, blue):
        self.np[3] = (red, green, blue)
        self.np.show()

    # speed: {0-255}
    # direction: {0,1}
    def motor_left(self, speed=0, direction=0):
        buf = bytearray(3)
        buf[0] = 0x00
        buf[1] = direction
        buf[2] = speed
        i2c.write(0x10, buf)

    # speed: {0-255}
    # direction: {0,1}
    def motor_right(self, speed=0, direction=0):
        buf = bytearray(3)
        buf[0] = 0x02
        buf[1] = direction
        buf[2] = speed
        i2c.write(0x10, buf)

    # return: {0,1}
    def line_left(self):
        if pin13.read_digital():
            return 1
        else:
            return 0

    # return: {0,1}
    def line_right(self):
        if pin14.read_digital():
            return 1
        else:
            return 0

    # angle: {0-180}
    def servo_one(self, angle=0):
        buf = bytearray(2)
        buf[0] = 0x14
        buf[1] = angle
        i2c.write(0x10, buf)

    # angle: {0-180}
    def servo_two(self, angle=0):
        buf = bytearray(2)
        buf[0] = 0x15
        buf[1] = angle
        i2c.write(0x10, buf)

    # return: distance in cm
    def ultrasound_measure(self):
        pin1.write_digital(1)
        utime.sleep_us(10)
        pin1.write_digital(0)

        # wait for echo pin to become high
        timeout = utime.ticks_us()
        while True:
            pulseBegin = utime.ticks_us()
            if 1 == pin2.read_digital():
                break
            if (pulseBegin-timeout) > 5000:
                return -1
        # measure time until echo pin become low

        while True:
            pulseEnd = utime.ticks_us()
            if 0 == pin2.read_digital():
                break
            if (pulseEnd-pulseBegin) > 5000:
                return -2
        # Time = Width of Echo pulse in us
        x = pulseEnd - pulseBegin
        # Distance in cm = Time / 58
        d = x / 58
        return int(d)

# robot = Maqueen()








