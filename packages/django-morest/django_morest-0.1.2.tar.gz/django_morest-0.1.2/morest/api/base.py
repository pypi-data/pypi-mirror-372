import typing
import dataclasses
from uuid import uuid4
from django.http import JsonResponse
from rest_framework import status
from morest.core import MorestJSONEncoder


class Response(JsonResponse):
    def __init__(self, 
                    data: dict = None, 
                    status_code: int = 200, 
                    status = 'ok',
                    message: str = 'OK', 
                    error_details: dict = None, 
                **kwargs):
        from morest.middlewares.requestid import RequestID
        
        data = {
            "data": data,
            "status": status,
            "status_code": status_code,
            "request_id": RequestID.get(uuid4().hex),
            "message": message,
        }
        if not 200 <= status_code <= 299:
            data['error_details'] = error_details

        super().__init__(data, status=status_code, encoder=MorestJSONEncoder, **kwargs)

    @classmethod
    def validation_error(cls, error_details: dict, status_code: int = status.HTTP_400_BAD_REQUEST) -> "Response":
        return cls(
            status_code=status_code,
            status='validation_error',
            message='Request body or query params validation error',
            error_details=error_details
        )
    
    @classmethod
    def from_status(cls, status: typing.Literal['ok', 'fail', 'error']) -> "Response":
        status_to_code = {
            "ok": 200,
            "fail": 400,
            "error": 500
        }
        return cls(
            status_code=status_to_code[status],
            status=status,
            message=status.capitalize()
        )
    