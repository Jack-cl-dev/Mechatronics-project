import radio

# Multiplier applied to the base drive speeds in main.py.
SPEED_LEVELS = {1: 0.7, 2: 1.0, 3: 1.3}   # 1 = slowest, 2 = default, 3 = fastest
MIN_LEVEL = 1
MAX_LEVEL = 3


class SpeedControl:
    """Listens for '+'/'-' over radio and tracks a speed level (1-3).

    Call update() once per main-loop iteration, radio.receive() is
    non-blocking, so this never stalls the loop even if nothing's arrived.
    Ask me how I know we needed this to be called once per loop iteration,
    not in a while loop.
    """

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