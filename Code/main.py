from microbit import *
from maqueen import Maqueen
from sound_detect import SoundSwitch
from obstacle_detect import ObstacleDetector
import utime

# - Important commands -
# mpremote connect auto cp main.py :main.py
# mpremote connect auto run main.py

robot = Maqueen()
sound_switch = SoundSwitch()
detector = ObstacleDetector(robot, stop_distance=10)

# --- HARDWARE POLARITY ---
#   1 = WHITE surface (off the line)
#   0 = BLACK line    (on the line)
def on_line_left():
    return 0 if robot.line_left() else 1

def on_line_right():
    return 0 if robot.line_right() else 1

FWD = 0
BWD = 1

BASE_SPEED    = 85
CORRECT_OUTER = 70
CORRECT_INNER = 60
PIVOT_OUTER   = 80
PIVOT_INNER   = 30
SWEEP_SPEED   = 85

LOOP_DELAY_MS = 5
STAGE1_MS     = 100
STAGE2_MS     = 1200

last_side = 1
lost_since = None

last_display_ms = utime.ticks_ms()
DISPLAY_EVERY_MS = 200
GRAVITY = 1000


def drive(l_speed, l_dir, r_speed, r_dir):
    robot.motor_left(l_speed, l_dir)
    robot.motor_right(r_speed, r_dir)

while True:
    wheels_on = sound_switch.update()

    if not wheels_on:
        drive(0, FWD, 0, FWD)
        lost_since = None
        utime.sleep_ms(40)
        continue

    if detector.check():
        detector.react()
        continue

    left = on_line_left()
    right = on_line_right()

    if left == 1 and right == 1:
        drive(BASE_SPEED, FWD, BASE_SPEED, FWD)
        lost_since = None

    elif left == 1 and right == 0:
        last_side = 1
        drive(CORRECT_INNER, FWD, CORRECT_OUTER, FWD)
        lost_since = None

    elif left == 0 and right == 1:
        last_side = -1
        drive(CORRECT_OUTER, FWD, CORRECT_INNER, FWD)
        lost_since = None

    else:
        if lost_since is None:
            lost_since = utime.ticks_ms()

        lost_for = utime.ticks_diff(utime.ticks_ms(), lost_since)

        if lost_for < STAGE1_MS:
            if last_side >= 0:
                drive(PIVOT_INNER, FWD, PIVOT_OUTER, FWD)
            else:
                drive(PIVOT_OUTER, FWD, PIVOT_INNER, FWD)

        elif lost_for < STAGE2_MS:
            if last_side >= 0:
                drive(PIVOT_INNER, BWD, PIVOT_OUTER, FWD)
            else:
                drive(PIVOT_OUTER, FWD, PIVOT_INNER, BWD)

        else:
            if last_side >= 0:
                drive(SWEEP_SPEED, BWD, SWEEP_SPEED, FWD)
            else:
                drive(SWEEP_SPEED, FWD, SWEEP_SPEED, BWD)

    now = utime.ticks_ms()
    if utime.ticks_diff(now, last_display_ms) >= DISPLAY_EVERY_MS:
        last_display_ms = now
        mag = accelerometer.get_strength()
        motion = abs(mag - GRAVITY)
        rows = motion // 200
        if rows > 5:
            rows = 5
        parts = []
        for r in range(5):
            if r >= (5 - rows):
                parts.append("99999")
            else:
                parts.append("00000")
        display.show(Image(":".join(parts)))

    utime.sleep_ms(LOOP_DELAY_MS)
