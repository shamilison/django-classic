from rest_framework.views import exception_handler

__author__ = 'shamilsakib'

import logging
from django_classic.logging.classic_logger import ClassicLogger

logging.setLoggerClass(ClassicLogger)
logger = logging.getLogger(__name__)


def classic_api_error_handler(exc, *args):
    logger.exception(exc)
    response = exception_handler(exc, *args)
    if response is not None:
        response.data['status_code'] = response.status_code
    return response
