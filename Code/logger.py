class Logger:
    def __init__(self, path=None):
        pass

    def log(self, tag, value):
        print("{}:{}".format(tag, value))

    def close(self):
        pass

log = Logger()