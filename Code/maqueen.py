from microbit import *
import neopixel
import utime
class Maqueen:
    def __init__(s):
        i2c.init()
        s.np = neopixel.NeoPixel(pin15, 4)
        pin1.write_digital(0)
        s._lt = 0
        s._ld = -1
    def led_left(s, v): pin8.write_digital(v)
    def led_right(s, v): pin12.write_digital(v)
    def _rgb(s, i, red, green, blue):
        s.np[i] = (red, green, blue)
        s.np.show()
    def rgb_front_left(s, red, green, blue): s._rgb(0, red, green, blue)
    def rgb_rear_left(s, red, green, blue): s._rgb(1, red, green, blue)
    def rgb_rear_right(s, red, green, blue): s._rgb(2, red, green, blue)
    def rgb_front_right(s, red, green, blue): s._rgb(3, red, green, blue)
    def _w(s, buf, attempts=6, retry_delay_ms=25):
        last_error = None
        for _ in range(attempts):
            try:
                i2c.write(0x10, buf)
                return
            except OSError as e:
                last_error = e
                utime.sleep_ms(retry_delay_ms)
        raise last_error
    def _motor(s, reg, speed, direction):
        buf = bytearray(3)
        buf[0] = reg
        buf[1] = direction
        buf[2] = speed
        s._w(buf)
    def motor_left(s, speed=0, direction=0): s._motor(0x00, speed, direction)
    def motor_right(s, speed=0, direction=0): s._motor(0x02, speed, direction)
    def line_left(s): return 1 if pin13.read_digital() else 0
    def line_right(s): return 1 if pin14.read_digital() else 0
    def _servo(s, reg, angle):
        buf = bytearray(2)
        buf[0] = reg
        buf[1] = angle
        s._w(buf)
    def servo_one(s, angle=0): s._servo(0x14, angle)
    def servo_two(s, angle=0): s._servo(0x15, angle)
    def ultrasound_measure(s):
        W = 5000
        GAP = 60000
        if utime.ticks_diff(utime.ticks_us(), s._lt) < GAP:
            return s._ld
        t0 = utime.ticks_us()
        while pin2.read_digital() == 1:
            if utime.ticks_diff(utime.ticks_us(), t0) > W:
                break
        pin1.write_digital(1)
        utime.sleep_us(10)
        pin1.write_digital(0)
        s._lt = utime.ticks_us()
        t1 = utime.ticks_us()
        while pin2.read_digital() == 0:
            if utime.ticks_diff(utime.ticks_us(), t1) > W:
                s._ld = -1
                return -1
        t2 = utime.ticks_us()
        while pin2.read_digital() == 1:
            if utime.ticks_diff(utime.ticks_us(), t2) > W:
                s._ld = -2
                return -2
        t3 = utime.ticks_us()
        d = int(utime.ticks_diff(t3, t2) / 58)
        s._ld = d
        return d
