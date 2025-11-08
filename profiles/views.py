"""Views for profile management."""

from rest_framework import permissions, viewsets
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from .models import SunProfile
from .serializers import SunProfileSerializer, UserProfileSerializer


class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.userprofile


class SunProfileViewSet(viewsets.ModelViewSet):
    serializer_class = SunProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SunProfile.objects.filter(user=self.request.user).order_by("-is_primary", "name")

    def perform_create(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_primary:
            return Response(
                {"detail": "Primary profile cannot be deleted."},
                status=HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)
