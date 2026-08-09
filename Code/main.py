from microbit import *
from maqueen import Maqueen
from sound_detect import SoundSwitch
from obstacle_detect import ObstacleDetector
from headlights import Headlights
from radio_recieve import SpeedControl
from statuslights import StatusLights
import utime
robot = Maqueen()
sound_switch = SoundSwitch()
headlights = Headlights(robot)
lights = StatusLights(robot)
def on_line_left():
	return 0 if robot.line_left() else 1
def on_line_right():
	return 0 if robot.line_right() else 1
def line_seen():
	return on_line_left() == 1 or on_line_right() == 1
detector = ObstacleDetector(robot, stop_distance=10, line_seen=line_seen)
speed_control = SpeedControl()
FWD = 0
BWD = 1
BASE_SPEED = 85
CORRECT_OUTER = 70
CORRECT_INNER = 60
PIVOT_OUTER = 80
PIVOT_INNER = 30
SWEEP_SPEED = 85
LOOP_DELAY_MS = 5
STAGE1_MS = 100
STAGE2_MS = 1200
last_side = 1
lost_since = None
prev_wheels_on = False
last_display_ms = utime.ticks_ms()
DISPLAY_EVERY_MS = 200
GRAVITY = 1000
def drive(l_speed, l_dir, r_speed, r_dir):
	scale = speed_control.multiplier
	robot.motor_left(min(255, int(l_speed * scale)), l_dir)
	robot.motor_right(min(255, int(r_speed * scale)), r_dir)
while True:
	speed_control.update()
	motors_running = sound_switch.state
	wheels_on = sound_switch.update(motors_running, detector.is_noisy())
	headlights.update()
	if wheels_on != prev_wheels_on:
		lights.flash_clap()
		prev_wheels_on = wheels_on
	if not wheels_on:
		drive(0, FWD, 0, FWD)
		lost_since = None
		lights.update(wheels_on, False)
		utime.sleep_ms(40)
		continue
	if detector.check():
		lights.update(wheels_on, True)
		detector.react()
		continue
	left = on_line_left()
	right = on_line_right()
	turning = None
	if left == 1 and right == 1:
		drive(BASE_SPEED, FWD, BASE_SPEED, FWD)
		lost_since = None
	elif left == 1 and right == 0:
		last_side = 1
		turning = 'left'
		drive(CORRECT_INNER, FWD, CORRECT_OUTER, FWD)
		lost_since = None
	elif left == 0 and right == 1:
		last_side = -1
		turning = 'right'
		drive(CORRECT_OUTER, FWD, CORRECT_INNER, FWD)
		lost_since = None
	else:
		if lost_since is None:
			lost_since = utime.ticks_ms()
		lost_for = utime.ticks_diff(utime.ticks_ms(), lost_since)
		if lost_for < STAGE1_MS:
			if last_side >= 0:
				turning = 'left'
				drive(PIVOT_INNER, FWD, PIVOT_OUTER, FWD)
			else:
				turning = 'right'
				drive(PIVOT_OUTER, FWD, PIVOT_INNER, FWD)
		elif lost_for < STAGE2_MS:
			if last_side >= 0:
				turning = 'left'
				drive(PIVOT_INNER, BWD, PIVOT_OUTER, FWD)
			else:
				turning = 'right'
				drive(PIVOT_OUTER, FWD, PIVOT_INNER, BWD)
		elif last_side >= 0:
			turning = 'left'
			drive(SWEEP_SPEED, BWD, SWEEP_SPEED, FWD)
		else:
			turning = 'right'
			drive(SWEEP_SPEED, FWD, SWEEP_SPEED, BWD)
	lights.update(wheels_on, False, turning)
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
			if r >= 5 - rows:
				parts.append('99999')
			else:
				parts.append('00000')
		display.show(Image(':'.join(parts)))
	utime.sleep_ms(LOOP_DELAY_MS)
