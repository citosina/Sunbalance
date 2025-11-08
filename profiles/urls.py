"""URL routes for profile operations."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SunProfileViewSet, UserProfileView

router = DefaultRouter()
router.register("items", SunProfileViewSet, basename="sunprofile")

urlpatterns = [
    path("user/", UserProfileView.as_view(), name="user-profile"),
    path("", include(router.urls)),
]
