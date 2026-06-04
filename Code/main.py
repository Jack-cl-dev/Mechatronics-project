from microbit import *
from macqueen import Maqueen
import utime

robot = Maqueen()

FORWARD = 80
TURN = 40
BIAS = 10

last_left_speed = 0
last_right_speed = 0
last_left_dir = 0
last_right_dir = 0

from microbit import *

smirk = Image(
    "00000:"
    "09090:"
    "00000:"
    "00009:"
    "09990"
)

display.show(smirk)

while True:
    left = robot.line_left()     # 0 = black, 1 = white
    right = robot.line_right()   # 0 = black, 1 = white

    # --- BOTH BLACK → GO STRAIGHT ---
    if left == 0 and right == 0:
        L = FORWARD - BIAS
        R = FORWARD
        LD = 0
        RD = 0

    # --- LEFT WHITE → TURN LEFT (correct direction) ---
    elif left == 1 and right == 0:
        L = TURN
        R = TURN
        LD = 1      # left wheel backward
        RD = 0      # right wheel forward

    # --- RIGHT WHITE → TURN RIGHT (correct direction) ---
    elif left == 0 and right == 1:
        L = TURN
        R = TURN
        LD = 0      # left wheel forward
        RD = 1      # right wheel backward

    # --- BOTH WHITE → KEEP LAST ACTION ---
    else:
        L = last_left_speed
        R = last_right_speed
        LD = last_left_dir
        RD = last_right_dir

    robot.motor_left(L, LD)
    robot.motor_right(R, RD)

    last_left_speed = L
    last_right_speed = R
    last_left_dir = LD
    last_right_dir = RD

    utime.sleep_ms(10)
