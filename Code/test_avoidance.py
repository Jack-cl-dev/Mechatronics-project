# Standalone test rig for obstacle detection + avoidance.
#
# Deliberately does NOT run the line follower or the clap switch, so a failed
# avoidance manoeuvre can't be blamed on either of those.
#
# Deploy it with (either way it lands on the board AS main.py, because that's
# the only name the micro:bit auto-runs):
#   Linux:    ./deploy.sh test_avoidance.py
#   Windows:  double-click deploy.bat, then pick option 2
#
# Controls:  A = start/resume driving (3s countdown)   B = stop
# The serial console prints what the avoidance routine is deciding.

from microbit import *
from maqueen import Maqueen
from obstacle_detect import ObstacleDetector
from compass import Compass
import utime

CRUISE_SPEED = 80
FWD = 0
STATUS_EVERY_MS = 250

robot = Maqueen()
compass_helper = Compass()

# On this robot the line sensors read 1 = white, 0 = black line.
def line_seen():
    return robot.line_left() == 0 or robot.line_right() == 0

detector = ObstacleDetector(robot, stop_distance=10, line_seen=line_seen)


def stop():
    robot.motor_left(0, 0)
    robot.motor_right(0, 0)


def wait_for_start():
    """Block until A is pressed, then count down so the robot can be put down."""
    stop()
    display.show(Image.ARROW_E)
    print("[test] press A to drive")
    while not button_a.was_pressed():
        utime.sleep_ms(50)
    for count in (3, 2, 1):
        display.show(str(count))
        utime.sleep_ms(700)
    display.clear()


print("[test] obstacle avoidance rig")
if not compass_helper.is_ready():
    print("[test] calibrating compass -- hold the board away from the motors")
compass_helper.ensure_calibrated()
print("[test] compass ready:", compass_helper.is_ready())

wait_for_start()
last_status = utime.ticks_ms()

while True:
    if button_b.was_pressed():
        stop()
        display.show(Image.NO)
        print("[test] stopped")
        wait_for_start()
        last_status = utime.ticks_ms()

    if detector.check():
        stop()
        display.show(Image.SURPRISED)
        print("[test] obstacle confirmed, reacting")
        result = detector.react()
        print("[test] avoidance result:", result)
        print("[test] heading now:", int(compass_helper.upright_heading()))
        display.clear()
        continue

    robot.motor_left(CRUISE_SPEED, FWD)
    robot.motor_right(CRUISE_SPEED, FWD)

    now = utime.ticks_ms()
    if utime.ticks_diff(now, last_status) >= STATUS_EVERY_MS:
        last_status = now
        print("[test] distance:", robot.ultrasound_measure(),
              "heading:", int(compass_helper.upright_heading()))

    utime.sleep_ms(10)
