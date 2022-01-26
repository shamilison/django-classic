import logging

from django.conf import settings


class ClassicLogger(logging.getLoggerClass()):

    def __init__(self, name):
        """
        Initialize the logger with a name and an optional level.
        """
        super(ClassicLogger, self).__init__(name=name, level="INFO")

    def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        super(ClassicLogger, self).info(msg, *args, **kwargs)
        if settings.CONSOLE_PRINT:
            print(msg)

    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        super(ClassicLogger, self).debug(msg, *args, **kwargs)
        if settings.CONSOLE_PRINT:
            print(msg)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.
        """
        if settings.DEBUG:
            raise Exception(msg)
        super(ClassicLogger, self).exception(msg, *args, exc_info=True, **kwargs)
        if settings.CONSOLE_PRINT:
            print(msg)
