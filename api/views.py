from django.shortcuts import render


# Create your views here.


from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from rest_framework import generics, permissions
from .models import SunExposure
from .serializers import SunExposureSerializer

class SunExposureListCreate(generics.ListCreateAPIView):
    serializer_class = SunExposureSerializer
    permission_classes = [permissions.IsAuthenticated]  # Require authentication

    def get_queryset(self):
        return SunExposure.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Assign the logged-in user


# User Registration API
class RegisterUser(APIView):
    permission_classes = [AllowAny]  # Allow anyone to register

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)

# Login API (Generates JWT Token)
class LoginUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

import requests
import geocoder
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class UVIndexView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def get(self, request, latitude, longitude):
        API_KEY = "openuv-hdbvrm6kannli-io"  # Replace with your actual OpenUV API key
        url = f"https://api.openuv.io/api/v1/uv?lat={latitude}&lng={longitude}"
        headers = {"x-access-token": API_KEY}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return Response(response.json())  # Return UV data as JSON
        else:
            return Response({"error": "Failed to fetch UV data"}, status=response.status_code)

class SmartLocationUVIndexView(APIView):
    permission_classes = [IsAuthenticated]  # Require authentication

    def get(self, request):
        # Get optional GPS coordinates from frontend
        latitude = request.query_params.get('lat', None)
        longitude = request.query_params.get('lon', None)

        # If no GPS coordinates are provided, fallback to IP-based location
        if not latitude or not longitude:
            g = geocoder.ip('me')  # Use IP to get approximate location
            if g.latlng:
                latitude, longitude = g.latlng
            else:
                return Response({"error": "Unable to determine location"}, status=400)

        # Fetch UV index data from OpenUV API
        API_KEY = "YOUR_OPENUV_API_KEY"  # Replace with your actual OpenUV API key
        url = f"https://api.openuv.io/api/v1/uv?lat={latitude}&lng={longitude}"
        headers = {"x-access-token": API_KEY}

        uv_response = requests.get(url, headers=headers)
        
        if uv_response.status_code == 200:
            uv_data = uv_response.json()
            return Response({
                "location": {"latitude": latitude, "longitude": longitude},
                "uv_data": uv_data
            })
        else:
            return Response({"error": "Failed to fetch UV data"}, status=uv_response.status_code)

