from microbit import *
from maqueen import Maqueen
from sound_detect import SoundSwitch
from obstacle_detect import ObstacleDetector
import utime

robot = Maqueen()
sound_switch = SoundSwitch()
detector = ObstacleDetector(robot, stop_distance=10)

FORWARD = 90
TURN_FAST = 60
TURN_SLOW = 40

while True:
    motors_running = sound_switch.state
    horn_active = detector.horn_active

    wheels_on = sound_switch.update(motors_running, horn_active)

    if not wheels_on:
        robot.motor_left(0, 0)
        robot.motor_right(0, 0)
        utime.sleep_ms(40)
        continue

    if detector.check():
        detector.react()
        continue

    left = robot.line_left()
    right = robot.line_right()

    if right == 1 and left == 1:
        L_speed = FORWARD
        L_dir = 0
        R_speed = FORWARD
        R_dir = 0

    elif right == 1 and left == 0:
        L_speed = TURN_SLOW
        L_dir = 1
        R_speed = TURN_FAST
        R_dir = 0

    elif right == 0 and left == 1:
        L_speed = TURN_FAST
        L_dir = 0
        R_speed = TURN_SLOW
        R_dir = 1

    else:
        R_speed = TURN_SLOW
        R_dir = 1
        L_speed = TURN_SLOW
        L_dir = 1

    robot.motor_left(L_speed, L_dir)
    utime.sleep_ms(1)
    robot.motor_right(R_speed, R_dir)

    utime.sleep_ms(10)
