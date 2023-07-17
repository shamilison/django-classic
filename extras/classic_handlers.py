from django.http import JsonResponse
from jwt import exceptions
from rest_framework.status import HTTP_403_FORBIDDEN
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
    else:
        _auth_error = isinstance(exc, exceptions.InvalidSignatureError) \
                      or isinstance(exc, exceptions.ExpiredSignatureError) \
                      or isinstance(exc, exceptions.InvalidTokenError) \
                      or isinstance(exc, exceptions.ExpiredSignatureError) \
                      or isinstance(exc, exceptions.ExpiredSignatureError)
        if _auth_error:
            response = JsonResponse(data={
                "message": str(exc),
                "success": False,
            }, status=HTTP_403_FORBIDDEN)
    return response
