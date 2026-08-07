import utime

LOG_PATH = "avoid_log.csv"
FLUSH_EVERY = 10

class Logger:
    def __init__(self, path=LOG_PATH):
        self.path = path
        self._count = 0
        # Fresh file each run so old runs don't get mixed in.
        with open(self.path, "w") as f:
            f.write("ms,tag,value\n")

    def log(self, tag, value):
        self._count += 1
        with open(self.path, "a") as f:
            f.write("{},{},{}\n".format(utime.ticks_ms(), tag, value))
        # Reopening every call costs time but guarantees nothing is lost if
        # the bot resets mid-run -- fine for a short test, not for production.

log = Logger()