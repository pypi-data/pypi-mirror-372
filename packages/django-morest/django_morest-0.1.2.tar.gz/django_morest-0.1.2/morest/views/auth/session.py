import json

from django.http import HttpRequest
from django.contrib.auth import login, logout

from rest_framework.views import APIView
from rest_framework import permissions

from morest.serializers import LoginSerializer, UserSerializer
from morest.api import Response


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request: HttpRequest):
        return Response(UserSerializer().to_representation(request.user))

    def post(self, request: HttpRequest):
        serializer = LoginSerializer(
            data=json.loads(self.request.body),
            context={'request': self.request}
        )
        if not serializer.is_valid():
            return Response.validation_error(serializer.errors)

        user = serializer.validated_data['user']
        login(
            request=request,
            user=user
        )

        return Response(UserSerializer().to_representation(user))


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: HttpRequest):
        logout(request)
        return Response.from_status('ok')
