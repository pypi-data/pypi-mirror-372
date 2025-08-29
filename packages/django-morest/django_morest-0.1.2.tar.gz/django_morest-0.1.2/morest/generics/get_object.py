import typing
from morest.errors import NotFoundError
from morest.core import get_queryset

T = typing.TypeVar("T")


def get_object_or_404(queryset: T, *args, **kwargs) -> T:
    queryset = get_queryset(queryset)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise NotFoundError.with_object_details(queryset.__name__, None)


def get_objects_or_404(qs: T, with_error_details: bool = False, **filters) -> T:
    try:
        return get_object_or_404(qs, **filters)
    except NotFoundError:    
        if with_error_details:
            raise NotFoundError.with_object_details(qs.__name__, filters)
        else:
            raise NotFoundError
