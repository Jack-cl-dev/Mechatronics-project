from microbit import *
import utime
CLAP_MARGIN = 70
MIN_CLAP_LEVEL = 200
MOTOR_NOISE_MARGIN = 60
MIN_STATE_TIME_MS = 1500
QUIET_TIME_NEEDED_MS = 300
BASELINE_LERP = 0.05
class SoundSwitch:
    def __init__(self):
        self.state = False
        self.last_trigger = 0
        self.armed = True
        self.quiet_since = None
        self.baseline = microphone.sound_level()
    def update(self, motors_running=False, ignore_sound=False):
        now = utime.ticks_ms()
        if ignore_sound:
            self.quiet_since = None
            return self.state
        sound = microphone.sound_level()
        threshold = max(MIN_CLAP_LEVEL, self.baseline + CLAP_MARGIN)
        if motors_running:
            threshold += MOTOR_NOISE_MARGIN
        if self.armed:
            if sound > threshold and utime.ticks_diff(now, self.last_trigger) > MIN_STATE_TIME_MS:
                self.state = not self.state
                self.last_trigger = now
                self.armed = False
                self.quiet_since = None
            elif not motors_running:
                self.baseline += (sound - self.baseline) * BASELINE_LERP
        else:
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
