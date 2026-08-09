from microbit import *
import utime

CLAP_MARGIN = 70             # how much louder than the current reference = a clap
MIN_CLAP_LEVEL = 200         # absolute floor, ignore anything below this
MIN_STATE_TIME_MS = 1500     # hard lockout: can't re-toggle sooner than this
QUIET_TIME_NEEDED_MS = 300   # must be quiet for this long (real time) to re-arm
BASELINE_LERP = 0.05         # how fast the ambient/motor baseline tracks

class SoundSwitch:
    def __init__(self):
        self.state = False
        self.last_trigger = 0
        self.armed = True
        self.quiet_since = None
        self.baseline = microphone.sound_level()       # ambient (motors off) reference
        self.motor_baseline = self.baseline             # motor-noise-floor reference
        self.was_motors_running = False

    def update(self, motors_running=False, ignore_sound=False):

        now = utime.ticks_ms()

        if ignore_sound:
            self.quiet_since = None
            self.was_motors_running = motors_running
            return self.state

        sound = microphone.sound_level()

        # The instant the wheels start spinning, snap the motor baseline to
        # the current reading instead of slowly drifting up from the old
        # ambient level -- avoids a false "clap" trigger on motor startup.
        if motors_running and not self.was_motors_running:
            self.motor_baseline = sound
        self.was_motors_running = motors_running

        reference = self.motor_baseline if motors_running else self.baseline
        threshold = max(MIN_CLAP_LEVEL, reference + CLAP_MARGIN)

        if self.armed:
            if sound > threshold and utime.ticks_diff(now, self.last_trigger) > MIN_STATE_TIME_MS:
                self.state = not self.state
                self.last_trigger = now
                self.armed = False
                self.quiet_since = None
            else:
                # keep whichever reference is currently active up to date,
                # so the threshold tracks the room OR the motor noise floor
                if motors_running:
                    self.motor_baseline += (sound - self.motor_baseline) * BASELINE_LERP
                else:
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
