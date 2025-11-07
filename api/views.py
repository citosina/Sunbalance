"""API views for the SunBalance application."""

from django.contrib.auth.models import User
from django.db.models import Avg, Sum
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import SunExposure
from .serializers import SunExposureSerializer
from .services import (
    LocationResolutionError,
    UVServiceError,
    estimate_vitamin_d,
    fetch_uv_index_data,
    resolve_coordinates,
)


class SunExposureListCreate(generics.ListCreateAPIView):
    """List the authenticated user's entries or create a new one."""

    serializer_class = SunExposureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SunExposure.objects.filter(user=self.request.user)

    def perform_create(self, serializer: SunExposureSerializer) -> None:
        duration = serializer.validated_data.get("duration_minutes")
        uv_index = serializer.validated_data.get("uv_index")
        vitamin_d = estimate_vitamin_d(duration_minutes=duration, uv_index=uv_index)
        serializer.save(user=self.request.user, vitamin_d_produced=vitamin_d)


class SunExposureSummaryView(APIView):
    """Provide aggregated insights for the authenticated user."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = SunExposure.objects.filter(user=request.user)
        aggregates = queryset.aggregate(
            total_minutes=Sum("duration_minutes"),
            average_uv_index=Avg("uv_index"),
            total_vitamin_d=Sum("vitamin_d_produced"),
        )

        last_entry = queryset.first()
        last_entry_payload = (
            SunExposureSerializer(last_entry).data if last_entry is not None else None
        )

        payload = {
            "total_sessions": queryset.count(),
            "total_minutes": aggregates["total_minutes"] or 0,
            "average_uv_index": round(aggregates["average_uv_index"] or 0, 2),
            "total_vitamin_d": round(aggregates["total_vitamin_d"] or 0, 2),
            "last_entry": last_entry_payload,
        }

        return Response(payload)


class RegisterUser(APIView):
    """Create a new user account."""

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already taken."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        User.objects.create_user(username=username, email=email, password=password)
        return Response(
            {"message": "User created successfully!"},
            status=status.HTTP_201_CREATED,
        )


class LoginUser(APIView):
    """Authenticate a user and return JWT tokens."""

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({"refresh": str(refresh), "access": str(refresh.access_token)})

        return Response(
            {"error": "Invalid credentials."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class UVIndexView(APIView):
    """Return UV data for provided coordinates."""

    permission_classes = [IsAuthenticated]

    def get(self, request, latitude: str | None = None, longitude: str | None = None):
        lat_param = latitude or request.query_params.get("lat")
        lon_param = longitude or request.query_params.get("lon")

        try:
            lat, lon = resolve_coordinates(lat_param, lon_param)
            uv_data = fetch_uv_index_data(lat, lon)
        except LocationResolutionError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except UVServiceError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({"location": {"latitude": lat, "longitude": lon}, "uv_data": uv_data})


class SmartLocationUVIndexView(APIView):
    """Return UV index based on GPS parameters or fallback to IP location."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        lat_param = request.query_params.get("lat")
        lon_param = request.query_params.get("lon")

        try:
            lat, lon = resolve_coordinates(lat_param, lon_param)
            uv_data = fetch_uv_index_data(lat, lon)
        except LocationResolutionError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except UVServiceError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({"location": {"latitude": lat, "longitude": lon}, "uv_data": uv_data})
