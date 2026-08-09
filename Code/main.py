from microbit import *
from maqueen import Maqueen
from sound_detect import SoundSwitch
from obstacle_detect import ObstacleDetector
from headlights import Headlights
from radio_recieve import SpeedControl
import utime

# - Important commands -
# Every module imported below has to be on the device, not just main.py, so use
# the deploy script from the repo root rather than copying one file:
#   Linux: ./deploy.sh
#   Windows:  double-click deploy.bat and pick option 1
# To test obstacle avoidance on its own (no line following, no clap switch):
#   Linux: /deploy.sh test_avoidance.py
#   Windows:  double-click deploy.bat and pick option 2

robot = Maqueen()
sound_switch = SoundSwitch()
headlights = Headlights(robot)


# --- HARDWARE POLARITY ---
# On this robot the line sensors read:
#   1 = WHITE surface (off the line)
#   0 = BLACK line    (on the line)
# The helpers below invert that so the rest of the code can use the
# intuitive convention:  on_line == 1 means "this sensor is over the line".
def on_line_left():
    return 0 if robot.line_left() else 1

def on_line_right():
    return 0 if robot.line_right() else 1

def line_seen():
    return on_line_left() == 1 or on_line_right() == 1

detector = ObstacleDetector(robot, stop_distance=10, line_seen=line_seen)
speed_control = SpeedControl()  # listens for '+'/'-' over radio, non-blocking

# Direction constants
FWD = 0      # direction bit for forward
BWD = 1      # direction bit for reverse

#  Speed tuning (0-255)
BASE_SPEED    = 85    # cruising speed when centred on the line
CORRECT_OUTER = 70    # outer wheel during a gentle correction
CORRECT_INNER = 60    # inner wheel during a gentle correction (still forward)
PIVOT_OUTER   = 80    # outer wheel during a search pivot
PIVOT_INNER   = 30    # inner wheel during a search pivot (kept forward, gentle)
SWEEP_SPEED   = 85    # wheel speed during the wide recovery rotation

#  Search / recovery timing (milliseconds)
LOOP_DELAY_MS = 5     # small delay to avoid oscillating faster than useful
STAGE1_MS     = 100   # gentle curved search toward last-seen side (normal curves)
STAGE2_MS     = 1200  # sharper in-place pivot (abrupt bends)

# +1 => line was last on the LEFT, -1 => last on the RIGHT.
last_side = 1
# Timestamp of when we first lost the line (None => currently on it).
lost_since = None
prev_wheels_on = False

# --- Motion display (accelerometer) ---
last_display_ms = utime.ticks_ms()
DISPLAY_EVERY_MS = 200   # refresh the screen 5x/second, not every loop
GRAVITY = 1000           # ~1000 mg is always present from gravity


def drive(l_speed, l_dir, r_speed, r_dir):
    scale = speed_control.multiplier
    robot.motor_left(min(255, int(l_speed * scale)), l_dir)
    robot.motor_right(min(255, int(r_speed * scale)), r_dir)

while True:
    speed_control.update()  # non-blocking -- picks up a pending '+'/'-' if any
    motors_running = sound_switch.state
    # react() blocks, so horn_active is never True by the time we get here --
    # is_noisy() covers the settling period after it instead.
    wheels_on = sound_switch.update(motors_running, detector.is_noisy())
    headlights.update()

    if wheels_on != prev_wheels_on:

        prev_wheels_on = wheels_on

    if not wheels_on:
        drive(0, FWD, 0, FWD)
        lost_since = None

        utime.sleep_ms(40)
        continue

    if detector.check():

        detector.react()
        continue

    left = on_line_left()      # 1 = on the line, 0 = off the line
    right = on_line_right()
    turning = None

    if left == 1 and right == 1:
        # Centred on the line -> drive straight and reset the lost timer.
        drive(BASE_SPEED, FWD, BASE_SPEED, FWD)
        lost_since = None

    elif left == 1 and right == 0:
        # Line under the LEFT sensor -> curve left. Both wheels forward
        # for a smooth, stable correction.
        last_side = 1
        turning = "left"
        drive(CORRECT_INNER, FWD, CORRECT_OUTER, FWD)
        lost_since = None

    elif left == 0 and right == 1:
        # Line under the RIGHT sensor -> curve right.
        last_side = -1
        turning = "right"
        drive(CORRECT_OUTER, FWD, CORRECT_INNER, FWD)
        lost_since = None

    else:
        # Both off the line, we assume that the line is lost. Pivot toward the side the line
        # was last seen on, escalating the search the longer it stays lost.
        if lost_since is None:
            lost_since = utime.ticks_ms()

        lost_for = utime.ticks_diff(utime.ticks_ms(), lost_since)

        if lost_for < STAGE1_MS:
            # Stage 1: gentle CURVED search - keep creeping forward while
            # turning toward the last-seen side. On a curved track the line
            # is usually just ahead and to one side, so this re-acquires it
            # smoothly without whipping past it.
            if last_side >= 0:   # line was on the left -> curve left
                turning = "left"
                drive(PIVOT_INNER, FWD, PIVOT_OUTER, FWD)
            else:                 # line was on the right -> curve right
                turning = "right"
                drive(PIVOT_OUTER, FWD, PIVOT_INNER, FWD)

        elif lost_for < STAGE2_MS:
            # Stage 2: sharper in-place pivot for genuinely abrupt bends.
            if last_side >= 0:
                turning = "left"
                drive(PIVOT_INNER, BWD, PIVOT_OUTER, FWD)
            else:
                turning = "right"
                drive(PIVOT_OUTER, FWD, PIVOT_INNER, BWD)

        else:
            # Stage 3: full rotational sweep in the last-known direction,
            if last_side >= 0:
                turning = "left"
                drive(SWEEP_SPEED, BWD, SWEEP_SPEED, FWD)
            else:
                turning = "right"
                drive(SWEEP_SPEED, FWD, SWEEP_SPEED, BWD)



    # --- Update the speed/motion display (throttled, never blocks driving) ---
    now = utime.ticks_ms()
    if utime.ticks_diff(now, last_display_ms) >= DISPLAY_EVERY_MS:
        last_display_ms = now
        # Total acceleration magnitude (includes gravity), in milli-g.
        mag = accelerometer.get_strength()
        # Remove the ~1g baseline so a still robot reads near zero.
        motion = abs(mag - GRAVITY)
        # Map motion onto 0..5 rows of a vertical bar graph.
        rows = motion // 200
        if rows > 5:
            rows = 5
        # Build the image explicitly, row by row, bottom-up.
        # Each row is either "99999" (lit) or "00000" (dark).
        parts = []
        for r in range(5):
            # Top row is index 0, bottom row is index 4.
            # Light a row if it's within the bottom `rows` rows.
            if r >= (5 - rows):
                parts.append("99999")
            else:
                parts.append("00000")
        display.show(Image(":".join(parts)))

    utime.sleep_ms(LOOP_DELAY_MS)