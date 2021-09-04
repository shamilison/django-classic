from rest_framework.views import exception_handler

__author__ = 'shamilsakib'


def classic_api_error_handler(exc, *args):
    response = exception_handler(exc, *args)
    if response is not None:
        response.data['status_code'] = response.status_code
    return response
