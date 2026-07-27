from microbit import *
from maqueen import Maqueen
from sound_detect import SoundSwitch
import utime

robot = Maqueen()
sound_switch = SoundSwitch()

FORWARD = 90
TURN_FAST = 60
TURN_SLOW = 40

last_left_speed = FORWARD
last_right_speed = FORWARD
last_left_dir = 0
last_right_dir = 0

display.show(Image.HAPPY)

while True:
    #  SOUND TOGGLE CHECK
    wheels_on = sound_switch.update()

    # MOTOR ON/OFF CONTROL 
    if not wheels_on:
        # Motors OFF
        robot.motor_left(0, 0)
        robot.motor_right(0, 0)
        display.show("0")
        utime.sleep_ms(40)
        continue
    else:
        display.show("1")

    # LINE SENSORS 
    left = robot.line_left()
    right = robot.line_right()

    # BOTH BLACK → GO STRAIGHT
    if right == 1 and left == 1:
        L_speed, L_dir = FORWARD, 0
        R_speed, R_dir = FORWARD, 0

    #  LEFT BLACK, RIGHT WHITE → VEER LEFT 
    elif right == 1 and left == 0:
        L_speed, L_dir = TURN_SLOW, 1
        R_speed, R_dir = TURN_FAST, 0

    # LEFT WHITE, RIGHT BLACK = VEER RIGHT 
    elif right == 0 and left == 1:
        L_speed, L_dir = TURN_FAST, 0
        R_speed, R_dir = TURN_SLOW, 1

    # BOTH WHITE = REVERSE 
    else:
        R_speed, R_dir = TURN_SLOW, 1
        L_speed, L_dir = TURN_SLOW, 1

    # APPLY MOTOR COMMANDS 
    robot.motor_left(L_speed, L_dir)
    utime.sleep_ms(1)
    robot.motor_right(R_speed, R_dir)

    # Store last values (except both white)
    if not (right == 0 and left == 0):
        last_left_speed = L_speed
        last_right_speed = R_speed
        last_left_dir = L_dir
        last_right_dir = R_dir

    utime.sleep_ms(10)

