import typing
from rest_framework import serializers
from django.db.models.query import QuerySet

from morest.core import search_in_queryset

T = typing.TypeVar("T")


class SearchSerializer(serializers.Serializer):
    q = serializers.CharField(required=False, write_only=True, allow_blank=True)

    def filter(self, qs: QuerySet[T], search_fields: typing.List[str]) -> QuerySet[T]:
        search_term = self.validated_data.get('q')
        return search_in_queryset(
            qs=qs,
            search_term=search_term,
            search_fields=search_fields
        )
