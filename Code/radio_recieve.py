import radio
SPEED_LEVELS = {1: 0.7, 2: 1.0, 3: 1.3}
MIN_LEVEL = 1
MAX_LEVEL = 3
class SpeedControl:
    def __init__(self, group=7, level=2):
        radio.config(group=group)
        radio.on()
        self.level = level
    def update(self):
        incoming = radio.receive()
        if incoming == '+':
            self.level = MIN_LEVEL if self.level >= MAX_LEVEL else self.level + 1
        elif incoming == '-':
            self.level = MAX_LEVEL if self.level <= MIN_LEVEL else self.level - 1
        return self.level
    @property
    def multiplier(self):
        return SPEED_LEVELS[self.level]
