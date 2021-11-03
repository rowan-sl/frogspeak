import logging, sys
from logging import getLoggerClass, addLevelName, NOTSET

#! custom thingy to redirect stdout to a logger
class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""
        self.realstdout = sys.__stdout__
        self.realstderr = sys.__stderr__

    def write(self, buf):
        # self.realstdout.write(buf)
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        # self.realstdout.flush()
        pass


#! custom logging levels

# ? logging level DETAIL: level #15 between DEBUG and INFO
DETAIL = 15


class CustomLoggerLevels(getLoggerClass()):
    def __init__(self, name, level=NOTSET):
        super().__init__(name, level)

        addLevelName(DETAIL, "DETAIL")

    def detail(self, msg, *args, **kwargs):
        if self.isEnabledFor(DETAIL):
            self._log(DETAIL, msg, args, **kwargs)
