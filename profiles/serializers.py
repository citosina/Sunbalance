"""Serializers for profile management."""

from collections.abc import Sequence

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import SunProfile, UserProfile


ALLOWED_TIME_WINDOWS = {"morning", "lunch", "afternoon", "evening"}


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id",
            "default_latitude",
            "default_longitude",
            "default_altitude_m",
            "default_skin_type",
            "preferred_time_windows",
        ]
        read_only_fields = ["id"]

    def validate_preferred_time_windows(self, value: Sequence[str]) -> list[str]:
        if not value:
            return list(ALLOWED_TIME_WINDOWS)
        invalid = [choice for choice in value if choice not in ALLOWED_TIME_WINDOWS]
        if invalid:
            raise serializers.ValidationError(
                f"Unsupported time windows: {', '.join(sorted(set(invalid)))}"
            )
        return list(dict.fromkeys(value))


class SunProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SunProfile
        fields = [
            "id",
            "name",
            "relationship",
            "age_group",
            "skin_type",
            "preferred_time_windows",
            "clothing_preferences",
            "sunscreen_spf",
            "hats",
            "location_latitude",
            "location_longitude",
            "altitude_m",
            "is_primary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_primary", "created_at", "updated_at"]

    def validate_preferred_time_windows(self, value: Sequence[str]) -> list[str]:
        if not value:
            return list(ALLOWED_TIME_WINDOWS)
        invalid = [choice for choice in value if choice not in ALLOWED_TIME_WINDOWS]
        if invalid:
            raise serializers.ValidationError(
                f"Unsupported time windows: {', '.join(sorted(set(invalid)))}"
            )
        return list(dict.fromkeys(value))

    def create(self, validated_data):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            raise serializers.ValidationError("Request user is required.")
        return SunProfile.objects.create(user=request.user, **validated_data)

    def update(self, instance: SunProfile, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
