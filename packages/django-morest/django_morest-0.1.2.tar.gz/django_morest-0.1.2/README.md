## django-morest - make your api more rest
### Need to install pycryptodome to be able to use EncryptedTextField

#### v0.0.1 - Basic functionality of api

## Documentation
### settings.py
```python3
INSTALLED_APPS = [
    ...
    "morest",
    ...
]

MIDDLEWARE = [
    "morest.middlewares.RequestIDMiddleware",
    "morest.middlewares.ExceptionMiddleware",
    ...
]

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': "morest.middlewares.DRFExceptionMiddleware",
}

```
### usage
#### test view
```python3
from django.http import HttpRequest
from rest_framework.views import APIView
from morest.api import Response


class TestView(APIView):
    def get(self, request: HttpRequest):
        return Response({
            "key": "value"
        })

```

#### response
```json
{
    "data": {
        "key": "value"
    },
    "status": "ok",
    "status_code": 200,
    "request_id": "4d06538d2d7b40db8e729757a363fe55",
    "message": "OK"
}
```