from rest_framework import serializers
from morest.utils import PaginationSerializer


def __build_response_serializer(serializer, many: bool = False) -> serializers.Serializer:
    name = getattr(getattr(serializer, 'Meta', object()), "ref_name", serializer.__name__)
    class Response(serializers.Serializer):
        def __init__(self, instance=None, data=..., **kwargs):
            if many:
                self._declared_fields["data"] = serializers.ListField(child=serializer())
            else:
                self._declared_fields["data"] = serializer()
            super().__init__(instance, data, **kwargs)

        status = serializers.CharField()
        status_code = serializers.IntegerField()
        request_id = serializers.CharField()
        message = serializers.CharField()

        class Meta:
            ref_name = f"Response{name}"
    return Response


def __build_paginator_serializer(rows_name: str, serializer) -> serializers.Serializer:
    name = getattr(getattr(serializer, 'Meta', object()), "ref_name", serializer.__name__)
    class Response(serializers.Serializer):
        def __init__(self, instance=None, data=..., **kwargs):
            self._declared_fields[rows_name] = serializers.ListField(child=serializer())
            super().__init__(instance, data, **kwargs)

        rows_count = serializers.IntegerField()
        pages_count = serializers.IntegerField()

        class Meta:
            ref_name = f"PaginatedResponse{name}"

    return Response


def schema(request_body: serializers.Serializer = None, request_query: serializers.Serializer = None, response: serializers.Serializer = None, **kwargs):
    from drf_yasg.utils import swagger_auto_schema
    response_serializer = None
    if response is not None:
        paginated_request = list(filter(lambda x: x is not None and issubclass(x, PaginationSerializer), (request_query, request_body)))
        if paginated_request:
            response_serializer = __build_response_serializer(
                __build_paginator_serializer(
                    rows_name=paginated_request[0].rows_name,
                    serializer=response
                )
            )
        else:
            many = False
            if isinstance(response, list):
                many = True
                response = response[0]
        
            response_serializer = __build_response_serializer(response, many=many)

    def wrap(func):
        func = swagger_auto_schema(
            request_body=request_body,
            query_serializer=request_query,
            responses={
                200: response_serializer
            },
            **kwargs
        )(func)
        return func
    return wrap
