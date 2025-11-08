"""Tests for profile endpoints."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import SunProfile


User = get_user_model()


class ProfileApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="sunny", password="strongpass")
        response = self.client.post(reverse("token_obtain_pair"), {"username": "sunny", "password": "strongpass"})
        self.access = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_user_profile_defaults_returned(self):
        response = self.client.get(reverse("user-profile"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("default_skin_type", response.data)

    def test_can_create_additional_profile(self):
        payload = {
            "name": "Luna",
            "relationship": "child",
            "age_group": "child",
            "skin_type": "II",
            "preferred_time_windows": ["morning", "afternoon"],
            "clothing_preferences": {"exposed_fraction": 0.25, "hats": True},
            "sunscreen_spf": 30,
            "hats": True,
            "altitude_m": 2000,
        }
        response = self.client.post(reverse("sunprofile-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SunProfile.objects.filter(user=self.user, name="Luna").exists())

    def test_primary_profile_cannot_be_deleted(self):
        primary = SunProfile.objects.get(user=self.user, is_primary=True)
        response = self.client.delete(reverse("sunprofile-detail", args=[primary.id]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
