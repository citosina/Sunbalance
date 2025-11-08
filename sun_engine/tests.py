"""Tests for the recommendation engine."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from django.test import SimpleTestCase

from .recommendations import compute_recommendation


class RecommendationTests(SimpleTestCase):
    def test_low_uv_allows_longer_window(self):
        rec = compute_recommendation(
            uv_index=2.0,
            skin_type="III",
            age_group="adult",
            altitude_m=0,
            clothing_coverage={"exposed_fraction": 0.3, "hats": True},
            sunscreen_spf=None,
        )
        self.assertEqual(rec["status"], "low_uv")
        self.assertGreaterEqual(rec["recommended_minutes_max"], rec["recommended_minutes_min"])

    def test_high_uv_child_triggers_caution(self):
        rec = compute_recommendation(
            uv_index=10.0,
            skin_type="II",
            age_group="toddler",
            altitude_m=2000,
            clothing_coverage={"exposed_fraction": 0.5, "hats": False},
            sunscreen_spf=30,
        )
        self.assertEqual(rec["status"], "avoid_now")
        self.assertTrue(any("caution" in warning.lower() for warning in rec["warnings"]))
        self.assertLessEqual(rec["recommended_minutes_max"], 10)


User = get_user_model()


class RecommendationEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="apiuser", password="StrongPass123")
        response = self.client.post(
            reverse("token_obtain_pair"), {"username": "apiuser", "password": "StrongPass123"}
        )
        self.access = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_today_endpoint_returns_payload(self):
        profile = self.user.sun_profiles.filter(is_primary=True).first()
        response = self.client.get(reverse("recommendation-today"), {"profile_id": profile.id})
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.data)
        self.assertIn("uv_index_now", response.data)
