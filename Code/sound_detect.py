from microbit import *
from maqueen import Maqueen
import utime

# Adjustable sensitivity (0–255)
CLAP_THRESHOLD = 180        # Loud clap/yell
DEBOUNCE_TIME_MS = 600      # Prevent double-trigger

class SoundSwitch:
    def __init__(self):
        self.state = False          # False = OFF, True = ON
        self.last_trigger = 0       # Time of last clap

    def update(self):
        #Check microphone and toggle state on loud sound.
        sound = microphone.sound_level()
        now = utime.ticks_ms()

        # Detect loud sound + debounce
        if sound > CLAP_THRESHOLD and (now - self.last_trigger) > DEBOUNCE_TIME_MS:
            self.state = not self.state
            self.last_trigger = now

            # Debug feedback (remove later if you want)
            if self.state:
                display.show("1")   # ON
            else:
                display.show("0")   # OFF

        return self.state


# Standalone test mode (runs if this file is executed directly)
sound_switch = SoundSwitch()

while True:
    sound_switch.update()
    utime.sleep_ms(50)
