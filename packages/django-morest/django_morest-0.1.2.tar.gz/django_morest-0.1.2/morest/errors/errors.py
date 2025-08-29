from .base import BaseError
from rest_framework import status


class InternalError(BaseError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = 'Internal server error'
    status = 'error'


class InsufficientBalanceError(BaseError):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    message = 'Insufficient balance, try to top up before commiting the action'
    status = 'insufficient_balance'

    @classmethod
    def with_balance_details(cls, current_balance: float, required_balance: float, **kwargs) -> "InsufficientBalanceError":
        return cls(
            error_details={
                "current_balance": current_balance,
                "required_balance": required_balance,
                **kwargs
            }
        )


class AlreadyExistsError(BaseError):
    status_code = status.HTTP_409_CONFLICT
    message = 'Data already exists'
    status = 'data_already_exists'

    @classmethod
    def with_object_details(cls, object: str, key: str, value: str) -> "AlreadyExistsError":
        return cls(
            message='{object} with {key} "{value}" already exists'.format(
                object=object, 
                key=key,
                value=value,
            ),
            error_details={
                "object": object,
                "key": key,
                "value": value,
            }
        )


class NotFoundError(BaseError):
    status_code = status.HTTP_404_NOT_FOUND
    message = 'Not found error'
    status = 'not_found'

    @classmethod
    def with_object_details(cls, object: str, filters: dict) -> "NotFoundError":
        return cls(
            message=f'{object} with {filters=} not found',
            error_details={
                "object": object,
                "filters": filters,
            }
        )
    

class ValidationError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'Validation error'
    status = 'validation_error'


class FieldNotFoundError(BaseError):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    message = 'Field not found'
    status = 'field_not_found'
    
