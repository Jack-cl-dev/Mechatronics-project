from microbit import *
import utime

CLAP_MARGIN = 70
MIN_CLAP_LEVEL = 200
MIN_STATE_TIME_MS = 1500     # hard lockout: can't re-toggle sooner than this
QUIET_TIME_NEEDED_MS = 300   # must be quiet for this long (real time) to re-arm

class SoundSwitch:
    def __init__(self):
        self.state = False
        self.last_trigger = 0
        self.armed = True
        self.quiet_since = None
        self.baseline = microphone.sound_level()

    def update(self):
        sound = microphone.sound_level()
        now = utime.ticks_ms()
        threshold = max(MIN_CLAP_LEVEL, self.baseline + CLAP_MARGIN)

        if self.armed:
            if sound > threshold and utime.ticks_diff(now, self.last_trigger) > MIN_STATE_TIME_MS:
                self.state = not self.state
                self.last_trigger = now
                self.armed = False
                self.quiet_since = None
            else:
                # track ambient baseline only while calm/armed
                self.baseline += (sound - self.baseline) * 0.05
        else:
            # can't even consider re-arming until the lockout time has passed
            if utime.ticks_diff(now, self.last_trigger) < MIN_STATE_TIME_MS:
                self.quiet_since = None
            elif sound < threshold:
                if self.quiet_since is None:
                    self.quiet_since = now
                elif utime.ticks_diff(now, self.quiet_since) >= QUIET_TIME_NEEDED_MS:
                    self.armed = True
                    self.quiet_since = None
            else:
                self.quiet_since = None

        return self.state
