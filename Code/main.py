from microbit import *
from maqueen import Maqueen
import utime

# - Important commands -
# mpremote connect auto cp main.py :main.py
# mpremote connect auto run main.py

robot = Maqueen()

FORWARD = 90
TURN_FAST = 60    # outer wheel speed during turn
TURN_SLOW = 40    # inner wheel REVERSED for sharper pivot

last_left_speed = FORWARD
last_right_speed = FORWARD
last_left_dir = 0
last_right_dir = 0

smirk = Image(
    "00000:"
    "09090:"
    "00000:"
    "00009:"
    "09990"
)

display.show(smirk)

while True:
    left = robot.line_left()     # Maybe: 1 = black, 0 = white?
    right = robot.line_right()

    # --- BOTH BLACK → GO STRAIGHT ---
    if right == 1 and left == 1:
        L_speed, L_dir = FORWARD, 0
        R_speed, R_dir = FORWARD, 0

    # --- LEFT BLACK, RIGHT WHITE → VEER LEFT ---
    elif right == 1 and left == 0:
        L_speed, L_dir = TURN_SLOW, 1
        R_speed, R_dir = TURN_FAST, 0

    # --- LEFT WHITE, RIGHT BLACK → VEER RIGHT ---
    elif right == 0 and left == 1:
        L_speed, L_dir = TURN_FAST, 0
        R_speed, R_dir = TURN_SLOW, 1

    # --- BOTH WHITE → REVERSE---
    else:
        R_speed, R_dir = TURN_SLOW, 1
        L_speed, L_dir = TURN_SLOW, 1

    # Apply motor commands
    robot.motor_left(L_speed, L_dir)
    utime.sleep_ms(1)
    robot.motor_right(R_speed, R_dir)

    # Store current values (but NOT when both white)
    if not (right == 0 and left == 0):
        last_left_speed = L_speed
        last_right_speed = R_speed
        last_left_dir = L_dir
        last_right_dir = R_dir

    utime.sleep_ms(10)
