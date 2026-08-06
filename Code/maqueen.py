from microbit import *
import neopixel
import utime

class Maqueen:

    def __init__(self):
        i2c.init()
        self.np = neopixel.NeoPixel(pin15, 4)
        pin1.write_digital(0)


    def led_left(self, value):
        pin8.write_digital(value)

    def led_right(self, value):
        pin12.write_digital(value)


    def rgb_front_left(self, red, green, blue):
        self.np[0] = (red, green, blue)
        self.np.show()

    def rgb_rear_left(self, red, green, blue):
        self.np[1] = (red, green, blue)
        self.np.show()


    def rgb_rear_right(self, red, green, blue):
        self.np[2] = (red, green, blue)
        self.np.show()

    def rgb_front_right(self, red, green, blue):
        self.np[3] = (red, green, blue)
        self.np.show()


    def motor_left(self, speed=0, direction=0):
        buf = bytearray(3)
        buf[0] = 0x00
        buf[1] = direction
        buf[2] = speed

    def motor_right(self, speed=0, direction=0):
        buf = bytearray(3)
        buf[0] = 0x02
        buf[1] = direction
        buf[2] = speed
        i2c.write(0x10, buf)


    def line_left(self):
        if pin13.read_digital():
            return 1
        else:
            return 0


    def line_right(self):
        if pin14.read_digital():
            return 1
        else:
            return 0

    def servo_one(self, angle=0):
        buf = bytearray(2)
        buf[0] = 0x14
        buf[1] = angle
        i2c.write(0x10, buf)


    def servo_two(self, angle=0):
        buf = bytearray(2)
        buf[0] = 0x15
        buf[1] = angle
        i2c.write(0x10, buf)


    def ultrasound_measure(self):
        pin1.write_digital(1)
        utime.sleep_us(10)
        pin1.write_digital(0)


        timeout = utime.ticks_us()
        while True:
            pulseBegin = utime.ticks_us()
            if 1 == pin2.read_digital():
                break
            if (pulseBegin-timeout) > 5000:
                return -1


        while True:
            pulseEnd = utime.ticks_us()
            if 0 == pin2.read_digital():
                break
            if (pulseEnd-pulseBegin) > 5000:
                return -2

        x = pulseEnd - pulseBegin

        d = x / 58
        return int(d)








