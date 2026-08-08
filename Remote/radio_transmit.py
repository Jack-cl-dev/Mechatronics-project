from microbit import *
import radio
input = None

radio.config(group=7,power=7)
radio.on()
while True:
    if button_a.was_pressed():
        input = "-"
        radio.send(input)
    if button_b.was_pressed():
        input = "+"
        radio.send(input)
