from microbit import *
import utime
import audio
from object_avoidance import ObjectAvoidance

# The mic keeps hearing the horn (and its own motors) for a moment after the
# reaction finishes, so tell the sound switch to ignore itself for this long.
NOISE_SETTLE_MS = 500


class ObstacleDetector:
    def __init__(self, robot, stop_distance=10, line_seen=None, avoider=None):
        self.robot = robot
        self.stop_distance = stop_distance
        self.horn_duration = 2000
        self.horn_active = False
        self.close_streak = 0
        self.confirm_needed = 3   # readings in a row before we trust it
        self.noisy_until = 0
        self.last_avoid_result = None
        # Built here by default so callers don't have to know about avoidance.
        if avoider is None:
            avoider = ObjectAvoidance(robot,
                                      stop_distance=stop_distance,
                                      line_seen=line_seen)
        self.avoider = avoider

    def check(self):
        distance = self.robot.ultrasound_measure()

        if distance <= 0 or distance > self.stop_distance:
            self.close_streak = 0
            return False

        self.close_streak += 1
        return self.close_streak >= self.confirm_needed

    def is_noisy(self):
        """True while our own horn/manoeuvre noise makes the mic untrustworthy."""
        return utime.ticks_diff(self.noisy_until, utime.ticks_ms()) > 0

    def react(self):
        """Sound the horn, then drive around the obstacle.

        Blocking, but every stage inside is time-bounded. Returns the avoidance
        result string ("line", "clear" or "reversed").
        """
        self.horn_active = True
        self.robot.motor_left(0, 0)
        self.robot.motor_right(0, 0)
        # wait=False, otherwise play() blocks for the length of the sound and
        # the sleep below adds a second, separate 2s pause on top of it.
        audio.play(Sound.SAD, wait=False)
        utime.sleep_ms(self.horn_duration)
        self.horn_active = False

        self.last_avoid_result = self.avoider.avoid_obstacle()

        self.noisy_until = utime.ticks_add(utime.ticks_ms(), NOISE_SETTLE_MS)
        self.close_streak = 0
        return self.last_avoid_result
