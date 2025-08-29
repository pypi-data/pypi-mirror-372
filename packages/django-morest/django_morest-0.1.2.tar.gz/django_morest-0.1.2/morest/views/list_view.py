import typing
from django.http import HttpRequest
from django.db.models.query import QuerySet
from rest_framework.views import APIView
from rest_framework.serializers import Serializer
from morest.utils import PaginationSerializer, SearchSerializer, OrderSerializer
from morest.api import Response
from morest.core import docs, get_queryset

class ListFilterView(APIView):
    queryset: QuerySet
    serializer: Serializer
    filter_serializer: Serializer = None
    search_fields: typing.List[str] = ()
    rows_name: str = None
    order_fields: list = None


    def get_queryset(self, request: HttpRequest, **kwargs) -> QuerySet:
        return get_queryset(self.queryset)
    
    def get_filter_serializer(self, request: HttpRequest, **kwargs) -> Serializer:
        return self.filter_serializer
    
    def get_filters(self, request: HttpRequest, filters: dict, **kwargs):
        s = self.get_filter_serializer(request)
        if issubclass(s, PaginationSerializer):
            filters.pop("page", None)
            filters.pop("limit", None)
        
        if issubclass(s, SearchSerializer):
            filters.pop("q", None)

        if issubclass(s, OrderSerializer):
            filters.pop("order_by", None)

        return filters
    
    def get_search_fields(self, request: HttpRequest, **kwargs):
        return self.search_fields
    
    def filter_queryset(self, request: HttpRequest, qs: QuerySet, filters: dict, **kwargs) -> QuerySet:
        return qs.filter(**filters).all()
    
    def get_search_result(self, request: HttpRequest, qs: QuerySet, search_fields: typing.List[str], filter_serializer: SearchSerializer, **kwargs) -> QuerySet:
        if not isinstance(filter_serializer, SearchSerializer):
            return qs
        return filter_serializer.filter(qs, search_fields)
    
    def get_order_fields(self, request: HttpRequest, **kwargs) -> typing.List[str]:
        return self.order_fields
    
    def get_serializer(self, request: HttpRequest) -> Serializer:
        return self.serializer
    
    def paginate(self, request: HttpRequest, filter_serializer: PaginationSerializer, qs: QuerySet):
        serializer = self.get_serializer(request)
        return filter_serializer.paginate(qs=qs, serializer=serializer, rows_name=self.rows_name)
    
    def serialize(self, request: HttpRequest, qs: QuerySet):
        serializer = self.get_serializer(request)
        return [serializer().to_representation(x) for x in qs]
    
    def order(self, request: HttpRequest, qs: QuerySet, order_fields: typing.List[str], filter_serializer: OrderSerializer, **kwargs):
        if not isinstance(filter_serializer, OrderSerializer):
            return qs
        return filter_serializer.order(qs, order_fields)

    def get_response_data(self, request: HttpRequest, qs: QuerySet, data: Serializer = None):
        if isinstance(data, PaginationSerializer):
            return self.paginate(request=request, filter_serializer=data, qs=qs)
        else:
            return self.serialize(request=request, qs=qs)
        
    def get(self, request: HttpRequest, **kwargs):
        qs = self.get_queryset(request, **kwargs)

        filter_serializer = self.get_filter_serializer(request, **kwargs)
        data = None

        if filter_serializer is not None:
            data = filter_serializer(data=request.GET)
            if not data.is_valid():
                return Response.validation_error(data.errors)
            
            filters = self.get_filters(request, data.validated_data.copy(), **kwargs)
            qs = self.filter_queryset(request, qs, filters, **kwargs)

            search_fields = self.get_search_fields(request, **kwargs)
            qs = self.get_search_result(request, qs, search_fields, data, **kwargs)

            order_fields = self.get_order_fields(request, **kwargs)
            qs = self.order(request, qs, order_fields, data, **kwargs)

        return Response(self.get_response_data(request, qs, data))
    
    @classmethod
    def as_view(cls, **initkwargs):
        try:
            class viewcls(cls):
                @docs.schema(request_query=cls.filter_serializer, response=cls.get_serializer(cls, None))
                def get(self, request):
                    return super().get(request)
            cls = viewcls
        except ImportError:
            pass
        return super().as_view(**initkwargs)
    
