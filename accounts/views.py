"""Views for authentication and user management."""

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserRegistrationSerializer, UserSerializer


class RegisterView(APIView):
    """Register a new user and return serialized data."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        payload = UserSerializer(user).data
        return Response(payload, status=status.HTTP_201_CREATED)
