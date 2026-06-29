from microbit import *
from maqueen import Maqueen

robot = Maqueen()

# Set a loud sound level that counts as a clap or yell.
# Normal room noise is usually around 20–60.
LOUD = 120

# Ignore the first reading because it jumps.
soundLevel = microphone.sound_level()
sleep(200)

# Keep track of whether the motors are running.
motors_on = False

# Stop motors at the start.
robot.motor_left(0, 0)
robot.motor_right(0, 0)

while True:
    # Read the current sound level.
    soundLevel = microphone.sound_level()
    print(soundLevel)

    # If the sound is loud enough, toggle motors.
    if soundLevel > LOUD:
        motors_on = not motors_on

        if motors_on:
            # Turn motors on (forward).
            robot.motor_left(150, 1)
            robot.motor_right(150, 1)
            display.show(Image.HAPPY)
        else:
            # Turn motors off.
            robot.motor_left(0, 0)
            robot.motor_right(0, 0)
            display.show(Image.NO)

        # Small delay so one clap doesn't trigger twice.
        sleep(600)

    sleep(100)
