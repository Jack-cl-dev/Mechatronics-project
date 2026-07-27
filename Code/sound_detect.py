from microbit import *
import utime

# Sensitivity settings
CLAP_THRESHOLD = 220          # Adjust if needed
DEBOUNCE_TIME_MS = 800        # Prevent double-trigger

class SoundSwitch:
    def __init__(self):
        self.state = False            # False = motors OFF, True = motors ON
        self.last_trigger = 0

    def update(self):
        #Detect loud sound and toggle motor state.
        sound = microphone.sound_level()
        now = utime.ticks_ms()

        if sound > CLAP_THRESHOLD and (now - self.last_trigger) > DEBOUNCE_TIME_MS:
            self.state = not self.state
            self.last_trigger = now

        return self.state

