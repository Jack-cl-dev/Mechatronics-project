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
    def _i2c_write(self, buf, attempts=6, retry_delay_ms=25):
        last_error = None
        for _ in range(attempts):
            try:
                i2c.write(0x10, buf)
                return
            except OSError as e:
                last_error = e
                utime.sleep_ms(retry_delay_ms)
        raise last_error
    def motor_left(self, speed=0, direction=0):
        buf = bytearray(3)
        buf[0] = 0x00
        buf[1] = direction
        buf[2] = speed
        self._i2c_write(buf)
    def motor_right(self, speed=0, direction=0):
        buf = bytearray(3)
        buf[0] = 0x02
        buf[1] = direction
        buf[2] = speed
        self._i2c_write(buf)
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
        self._i2c_write(buf)
    def servo_two(self, angle=0):
        buf = bytearray(2)
        buf[0] = 0x15
        buf[1] = angle
        self._i2c_write(buf)
    _last_trigger = 0
    _last_distance = -1
    def ultrasound_measure(self):
        MAX_ECHO_WAIT_US = 5000
        RETRIGGER_GAP_US = 60000
        since_last = utime.ticks_diff(utime.ticks_us(), self._last_trigger)
        if since_last < RETRIGGER_GAP_US:
            return self._last_distance
        drain_start = utime.ticks_us()
        while pin2.read_digital() == 1:
            if utime.ticks_diff(utime.ticks_us(), drain_start) > MAX_ECHO_WAIT_US:
                break
        pin1.write_digital(1)
        utime.sleep_us(10)
        pin1.write_digital(0)
        self._last_trigger = utime.ticks_us()
        start = utime.ticks_us()
        while pin2.read_digital() == 0:
            if utime.ticks_diff(utime.ticks_us(), start) > MAX_ECHO_WAIT_US:
                self._last_distance = -1
                return -1
        pulse_begin = utime.ticks_us()
        while pin2.read_digital() == 1:
            if utime.ticks_diff(utime.ticks_us(), pulse_begin) > MAX_ECHO_WAIT_US:
                self._last_distance = -2
                return -2
        pulse_end = utime.ticks_us()
        d = int(utime.ticks_diff(pulse_end, pulse_begin) / 58)
        self._last_distance = d
        return d