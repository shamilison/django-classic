import logging
import traceback

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
        _extras = kwargs.get("extra")
        if _extras and "message" in _extras:
            del _extras["message"]
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

    def exception(self, msg, *args, exc_info=True, send_email=False, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.
        """
        # if settings.DEBUG:
        #     raise Exception(msg)
        super(ClassicLogger, self).exception(msg, *args, exc_info=True, **kwargs)
        if settings.CONSOLE_PRINT:
            print(msg)
        if send_email:
            try:
                from django_classic.controllers.classic_mail import send_classic_email
                _traces = traceback.format_stack()[::-1]
                _error_trace = "<br>".join([_line.strip() for _line in _traces])
                send_classic_email(
                    f'{settings.ERROR_EMAIL_PREFIX}: {str(msg)}',
                    f'<b>Exception Alert:</b><br><br>{_error_trace}',
                    settings.EMAIL_DEFAULT_FROM, settings.EMAIL_ERROR_SEND_TO.split(','))
            except Exception as error:
                logging.exception(error)
