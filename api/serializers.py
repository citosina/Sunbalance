from rest_framework import serializers

from .models import SunExposure


class SunExposureSerializer(serializers.ModelSerializer):
    vitamin_d_produced = serializers.FloatField(read_only=True)

    class Meta:
        model = SunExposure
        fields = ["id", "date", "duration_minutes", "uv_index", "vitamin_d_produced"]
        read_only_fields = ["id", "date", "vitamin_d_produced"]

    def validate_duration_minutes(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than zero minutes.")
        return value

    def validate_uv_index(self, value: float) -> float:
        if value < 0:
            raise serializers.ValidationError("UV index cannot be negative.")
        return value

