import logging
from traceback import format_exc
from django.http import HttpRequest, HttpResponse
from django.conf import settings
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler
from morest.errors import BaseError, InternalError
from morest.api import Response


class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _handle_exception(self, exc):
        if isinstance(exc, BaseError):
            return exc.to_response()
        elif isinstance(exc, APIException):
            return Response(
                status=exc.detail.code,
                status_code=exc.status_code,
                message=str(exc.detail),
                error_details=exc.get_full_details(),
            )
        else:
            exception = format_exc()
            logging.error(exception)
            if settings.DEBUG:
                return InternalError(error_details={
                    "exception": exception,
                }).to_response()

            return InternalError().to_response()
        
    def __call__(self, request: HttpRequest):
        try:
            response: HttpResponse = self.get_response(request)
            return response
        except BaseException as e:
            return self._handle_exception(e)


def DRFExceptionMiddleware(exc, context):
    response = exception_handler(exc, context)
    if exc is not None:
        return ExceptionMiddleware(None)._handle_exception(exc)
    return response