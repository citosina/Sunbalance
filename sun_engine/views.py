"""API views exposing sun recommendations."""

from __future__ import annotations

from datetime import datetime, timezone

from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles.models import SunProfile
from uv_api.services import get_uv_data

from .recommendations import compute_recommendation

DEFAULT_LOCATION = {
    "latitude": 19.4326,
    "longitude": -99.1332,
    "altitude_m": 2250,
}

DISCLAIMER_TEXT = (
    "SunBalance provides conservative guidance and is not medical advice. "
    "Consult your doctor for personalised recommendations."
)


class TodayRecommendationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        profile_id = request.query_params.get("profile_id")
        profile = get_object_or_404(SunProfile, pk=profile_id, user=request.user)
        user_profile = request.user.userprofile

        latitude = profile.location_latitude or user_profile.default_latitude or DEFAULT_LOCATION["latitude"]
        longitude = profile.location_longitude or user_profile.default_longitude or DEFAULT_LOCATION["longitude"]
        altitude = profile.altitude_m or user_profile.default_altitude_m or DEFAULT_LOCATION["altitude_m"]

        uv_payload = get_uv_data(latitude, longitude)
        clothing = profile.clothing_preferences.copy()
        clothing.setdefault("hats", profile.hats)

        recommendation = compute_recommendation(
            uv_index=uv_payload.get("uv_index_now", 0.0),
            skin_type=profile.skin_type,
            age_group=profile.age_group,
            altitude_m=altitude,
            clothing_coverage=clothing,
            sunscreen_spf=profile.sunscreen_spf,
        )

        response_payload = {
            "profile_id": profile.id,
            "profile_name": profile.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": recommendation["status"],
            "recommended_minutes_min": recommendation["recommended_minutes_min"],
            "recommended_minutes_max": recommendation["recommended_minutes_max"],
            "warnings": recommendation.get("warnings", []),
            "suggested_windows": recommendation.get("suggested_windows", profile.preferred_time_windows),
            "uv_index_now": uv_payload.get("uv_index_now"),
            "uv_trend": uv_payload.get("uv_forecast", []),
            "data_quality": uv_payload.get("data_quality", "unknown"),
            "location": {"latitude": latitude, "longitude": longitude, "altitude_m": altitude},
            "preferred_time_windows": profile.preferred_time_windows,
            "disclaimer": DISCLAIMER_TEXT,
        }
        if "message" in uv_payload:
            response_payload["uv_message"] = uv_payload["message"]
        return Response(response_payload)
