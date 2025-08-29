import contextvars
from uuid import uuid4
from django.http import HttpRequest, HttpResponse

RequestID = contextvars.ContextVar('request_id')

class RequestIDMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request: HttpRequest):
    request_id = request.headers.get('Request-ID', uuid4().hex)
    RequestID.set(request_id)
    response: HttpResponse = self.get_response(request)
    response.headers['Request-ID'] = request_id
    return response
