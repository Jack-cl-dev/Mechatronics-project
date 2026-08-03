from microbit import *
import utime

CLAP_MARGIN = 70           # how much louder than background = a clap
MIN_CLAP_LEVEL = 200       # absolute floor, ignore anything below this
DEBOUNCE_TIME_MS = 700
QUIET_STREAK_NEEDED = 8    # consecutive quiet readings needed to re-arm

class SoundSwitch:
    def __init__(self):
        self.state = False
        self.last_trigger = 0
        self.armed = True
        self.quiet_streak = 0
        self.baseline = microphone.sound_level()

    def update(self):
        sound = microphone.sound_level()
        now = utime.ticks_ms()
        threshold = max(MIN_CLAP_LEVEL, self.baseline + CLAP_MARGIN)

        if self.armed:
            if sound > threshold and (now - self.last_trigger) > DEBOUNCE_TIME_MS:
                self.state = not self.state
                self.last_trigger = now
                self.armed = False
                self.quiet_streak = 0
            else:
                # slowly track quiet-room ambient level so threshold adapts
                self.baseline += (sound - self.baseline) * 0.05
        else:
            # require several consecutive quiet samples in a row, not just one,
            # so a single dip in motor noise can't immediately re-arm it
            if sound < threshold:
                self.quiet_streak += 1
                if self.quiet_streak >= QUIET_STREAK_NEEDED:
                    self.armed = True
                    self.quiet_streak = 0
            else:
                self.quiet_streak = 0

        return self.state
