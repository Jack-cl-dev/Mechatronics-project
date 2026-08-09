from microbit import *
import utime
from av_turn import TurnMixin
from av_drive import DriveMixin
SIDESTEP_DEG = 90
STEP_DRIVE_MS = 350
STEPS_BETWEEN_CHECKS = 3
REJOIN_DRIVE_MS = 2000
MAX_SIDESTEPS = 8
MANOEUVRE_TIMEOUT_MS = 20000
class ObjectAvoidance(TurnMixin, DriveMixin):
    def __init__(self, robot, stop_distance=10, line_seen=None, verbose=True):
        self.robot = robot
        self.stop_distance = stop_distance
        self.line_seen = line_seen
        self.verbose = verbose
        self._deadline = 0
        self.last_result = None
    def _log(self, message):
        if self.verbose:
            print("[avoid] " + message)
    def _stop(self):
        self.robot.motor_left(0, 0)
        self.robot.motor_right(0, 0)
    def _out_of_time(self):
        return utime.ticks_diff(self._deadline, utime.ticks_ms()) <= 0
    def _choose_side(self):
        self._turn(SIDESTEP_DEG)
        utime.sleep_ms(150)
        if self._is_clear(self._probe()):
            return 1
        self._turn(-2 * SIDESTEP_DEG)
        utime.sleep_ms(150)
        if self._is_clear(self._probe()):
            return -1
        return None
    def avoid_obstacle(self):
        self._log("avoiding obstacle")
        self._stop()
        self._deadline = utime.ticks_add(utime.ticks_ms(), MANOEUVRE_TIMEOUT_MS)
        side = self._choose_side()
        if side is None:
            self._log("boxed in, backing out")
            self._turn(-SIDESTEP_DEG)
            self._drive_forward(REJOIN_DRIVE_MS, stop_on_line=True)
            self._stop()
            self.last_result = "reversed"
            return self.last_result
        self._log("detour to the " + ("right" if side > 0 else "left"))
        detour = side * SIDESTEP_DEG
        steps = 0
        while steps < MAX_SIDESTEPS and not self._out_of_time():
            outcome = self._drive_forward(STEP_DRIVE_MS, stop_on_line=True)
            if outcome == "line":
                self._stop()
                self.last_result = "line"
                self._log("done: line")
                return self.last_result
            if outcome == "blocked":
                self._log("sidestep blocked after {} step(s)".format(steps))
                break
            steps += 1
            if steps % STEPS_BETWEEN_CHECKS != 0:
                continue
            self._turn(-detour)
            utime.sleep_ms(150)
            if self._is_clear(self._probe()):
                self._log("course clear after {} sidestep(s)".format(steps))
                outcome = self._drive_forward(REJOIN_DRIVE_MS, stop_on_line=True)
                self._stop()
                self.last_result = "line" if outcome == "line" else "clear"
                self._log("done: " + self.last_result)
                return self.last_result
            self._turn(detour)
        self._log("giving up after {} sidestep(s)".format(steps))
        self._turn(-detour)
        self._stop()
        self.last_result = "stuck"
        return self.last_result