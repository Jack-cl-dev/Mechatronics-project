import utime

LOG_PATH = "avoid_log.csv"

class Logger:
    def __init__(self, path=LOG_PATH):
        self.path = path
        # 'w' truncates once at startup; the handle then stays open for
        # the whole run, since 'a' isn't supported on this filesystem and
        # reopening per-call would mean re-writing the whole file each time.
        self._f = open(self.path, "w")
        self._f.write("ms,tag,value\n")
        self._f.flush()

    def log(self, tag, value):
        self._f.write("{},{},{}\n".format(utime.ticks_ms(), tag, value))
        self._f.flush()

    def close(self):
        self._f.close()
# I *hate* this microbit. Append is too complex a file operation apparently, so we have to run through all these steps
# just so we can write to an existing file. Every time I have to make an edit, I need to do it over ssh and recompile the whole thing.
# You can imagine I wasn't particularly thrilled to learn I have to spend 10 minutes editing the file again and getting it to the remote machine.
log = Logger()