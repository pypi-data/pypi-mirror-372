import typing
from rest_framework import serializers
from django.db.models.query import QuerySet
from django.core.exceptions import FieldError
from morest.errors import FieldNotFoundError

T = typing.TypeVar("T")


class OrderSerializer(serializers.Serializer):
    order_fields: typing.List[str] = None

    order_by = serializers.ListField(child=serializers.CharField(), required=False, write_only=True, allow_empty=True)
    
    def _validate_order_by(self, order_by: typing.List[str], order_fields: typing.List[str], **kwargs):
        if order_fields is None:
            order_fields = self.order_fields
            
        order_by = map(lambda x: x[1:] if x.startswith('-') else x, order_by)
        if len(set(order_by) - set(order_fields)) != 0:
            raise FieldNotFoundError
    
    def _order_by(self, qs: QuerySet[T], order_by: typing.List[str]) -> QuerySet[T]:
        try:
            return qs.order_by(*order_by)
        except FieldError:
            raise FieldNotFoundError
        
    def order(self, qs: QuerySet[T], order_fields: typing.List[str] = None, **kwargs) -> QuerySet[T]:
        order_by = self.validated_data.get('order_by')
        if order_by is None:
            return qs
        
        if order_fields is not None:
            self._validate_order_by(order_by, order_fields, **kwargs)

        return self._order_by(qs, order_by)
    
