from microbit import *
from maqueen import Maqueen
import utime

# - Important commands -
# mpremote connect auto cp main.py :main.py
# mpremote connect auto run main.py

robot = Maqueen()

FORWARD = 65
TURN_FAST =20   # boost outer wheel for sharper correction
TURN_SLOW = 0     # stop inner wheel completely for aggressive turn

last_left_speed = FORWARD
last_right_speed = FORWARD

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
        L = FORWARD
        R = FORWARD

    # --- LEFT BLACK, RIGHT WHITE → VEER LEFT ---
    elif left == 0 and right == 1:
        L = TURN_SLOW
        robot.motor_left(TURN_SLOW, 1)
        R = TURN_FAST

    # --- LEFT WHITE, RIGHT BLACK → VEER RIGHT ---
    elif left == 1 and right == 0:
        L = TURN_FAST
        robot.motor_right(TURN_SLOW, 1)
        R = TURN_SLOW

    # --- BOTH WHITE → KEEP LAST ACTION ---
    else:
        L = last_left_speed
        R = last_right_speed

    # Both wheels always go forward (direction = 0)
    robot.motor_left(L, 0)
    robot.motor_right(R, 0)

    last_left_speed = L
    last_right_speed = R

    utime.sleep_ms(10)

