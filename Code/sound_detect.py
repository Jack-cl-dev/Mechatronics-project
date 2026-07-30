from microbit import *
import utime

CLAP_THRESHOLD = 230
DEBOUNCE_TIME_MS = 900

class SoundSwitch:
    def __init__(self):
        self.state = False
        self.last_trigger = 0

    def update(self):
        level = microphone.sound_level()
        now = utime.ticks_ms()

        if level > CLAP_THRESHOLD and (now - self.last_trigger) > DEBOUNCE_TIME_MS:
            self.state = not self.state
            self.last_trigger = now

        return self.state
