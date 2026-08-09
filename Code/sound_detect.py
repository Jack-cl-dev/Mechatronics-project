from microbit import *
import utime

CLAP_MARGIN = 70             # how much louder than background = a clap
MIN_CLAP_LEVEL = 200         # absolute floor, ignore anything below this
MOTOR_NOISE_MARGIN = 60      # extra headroom needed while the wheels are turning
MIN_STATE_TIME_MS = 1500     # hard lockout: can't re-toggle sooner than this
QUIET_TIME_NEEDED_MS = 300   # must be quiet for this long (real time) to re-arm
BASELINE_LERP = 0.05         # how fast the ambient baseline tracks the room

class SoundSwitch:
    def __init__(self):
        self.state = False
        self.last_trigger = 0
        self.armed = True
        self.quiet_since = None
        self.baseline = microphone.sound_level() 

    def update(self, motors_running=False, ignore_sound=False):
        """Sample the mic and return the latch state (True = wheels enabled).

        motors_running -- the wheels are turning, so the robot is making its own
                          noise. The trigger threshold is raised and the ambient
                          baseline is frozen, otherwise motor hum slowly drags
                          the baseline up until no clap can ever clear it.
                          Should fix the issues we were seeing earlier.
        ignore_sound --   use when something is making noise (the horn), making the
                          sample untrustworthy. Hold state and don't let
                          the reading count toward re-arming.
        """
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
                # track ambient baseline only while calm, armed and quiet
                self.baseline += (sound - self.baseline) * BASELINE_LERP
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
