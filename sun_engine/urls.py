"""URL configuration for recommendation endpoints."""

from django.urls import path

from .views import TodayRecommendationView

urlpatterns = [
    path("today/", TodayRecommendationView.as_view(), name="recommendation-today"),
]
