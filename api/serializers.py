from rest_framework import serializers
from .models import SunExposure

class SunExposureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SunExposure
        fields = ['id', 'date', 'duration_minutes', 'uv_index', 'vitamin_d_produced']  # Exclude "user"

