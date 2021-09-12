import logging

from django.conf import settings


class ClassicLogger(logging.getLoggerClass()):

    def exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.
        """
        if not settings.DEBUG:
            super(ClassicLogger, self).exception(msg, *args, exc_info=True, **kwargs)
        else:
            raise Exception(msg)
