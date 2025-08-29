import math
import typing
from dataclasses import dataclass
from rest_framework import serializers
from django.db.models.manager import BaseManager
from django.db.models.query import QuerySet
from morest.errors import InternalError
from morest.core import get_queryset
T = typing.TypeVar("T")

@dataclass
class PaginatedSerializedData:
    rows: typing.List[typing.Union[dict, T]]
    rows_count: int
    pages_count: int


class PaginationSerializer(serializers.Serializer):
    rows_name = 'rows'

    page = serializers.IntegerField(required=False, min_value=1, write_only=True)
    limit = serializers.IntegerField(required=False, min_value=1, write_only=True)

    def paginate(self, qs: typing.Union[BaseManager[T], typing.List[T]], serializer: serializers.Serializer = None, rows_name: str = None, **kwargs) -> PaginatedSerializedData:
        if rows_name is None:
            rows_name = self.rows_name

        page = self.validated_data.get('page', 1)
        limit = self.validated_data.get('limit', 20)

        qs = get_queryset(qs)

        if isinstance(qs, list):
            total_rows_count = len(qs)
            rows = qs[(page-1)*limit:page*limit]
        elif isinstance(qs, QuerySet) or isinstance(qs, BaseManager):
            total_rows_count = qs.count()
            rows = qs.all()[(page-1)*limit:page*limit]
        else:
            raise InternalError
        
        obj_serializer = lambda obj: serializer().to_representation(obj, **kwargs) if serializer is not None else obj 

        data = PaginatedSerializedData(
            rows=[obj_serializer(x) for x in rows],
            rows_count=len(rows),
            pages_count=math.ceil(total_rows_count/limit)
        )
        data.__dataclass_fields__['rows'].name = rows_name
        setattr(data, rows_name, data.rows)
        return data

