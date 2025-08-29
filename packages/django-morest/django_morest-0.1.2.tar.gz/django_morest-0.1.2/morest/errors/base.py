from morest.api.base import Response


class BaseError(BaseException):
    def __init__(self, message: str = None, error_details: dict = None):
        self.message = message or self.message
        self.error_details = error_details or self.error_details
        super().__init__()

    status_code = 500
    message = 'error'
    status = 'error'
    error_details = None

    def to_response(self) -> Response:
        return Response(
            data=None,
            status_code=self.status_code,
            status=self.status,
            message=self.message,
            error_details=self.error_details,
        )

