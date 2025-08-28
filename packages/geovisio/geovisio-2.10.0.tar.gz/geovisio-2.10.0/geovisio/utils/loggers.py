import logging


class LoggingWithExtra(logging.LoggerAdapter):
    """Add some metadata to the log message"""

    def process(self, msg, kwargs):
        sep = " " if self.extra else ""
        return f"{self.extra if self.extra else ''}{sep}{msg}", kwargs


def getLoggerWithExtra(logger_name, extra):
    """Create a logger with extra information. Those information will be displayed in the log message"""
    return LoggingWithExtra(logging.getLogger(logger_name), extra)
