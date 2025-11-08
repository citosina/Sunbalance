"""Aggregate API routes for the SunBalance backend."""

from django.urls import include, path

urlpatterns = [
    path("auth/", include("accounts.urls")),
    path("profiles/", include("profiles.urls")),
    path("recommendation/", include("sun_engine.urls")),
]
