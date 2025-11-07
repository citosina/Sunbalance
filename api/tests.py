from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from .services import LocationResolutionError, UVServiceError, estimate_vitamin_d


class AuthenticationTests(APITestCase):
    def test_user_registration_requires_credentials(self):
        response = self.client.post(reverse("register"), {"username": "", "password": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_register_and_login(self):
        payload = {"username": "sunny", "password": "strongpassword"}
        response = self.client.post(reverse("register"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        login_response = self.client.post(reverse("login"), payload, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)

    def test_duplicate_registration_is_rejected(self):
        User.objects.create_user(username="sunny", password="password123")
        response = self.client.post(
            reverse("register"), {"username": "sunny", "password": "password123"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SunExposureTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="traveler", password="Secret123")
        login_response = self.client.post(
            reverse("login"), {"username": "traveler", "password": "Secret123"}, format="json"
        )
        self.access_token = login_response.data["access"]

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_authentication_required_for_exposure_endpoints(self):
        response = self.client.get(reverse("sun_exposure"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_create_and_list_exposures(self):
        self.authenticate()
        payload = {"duration_minutes": 20, "uv_index": 5.0}
        response = self.client.post(reverse("sun_exposure"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expected_vitamin_d = estimate_vitamin_d(20, 5.0)
        self.assertAlmostEqual(response.data["vitamin_d_produced"], expected_vitamin_d)

        list_response = self.client.get(reverse("sun_exposure"))
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

    def test_summary_endpoint_returns_aggregated_metrics(self):
        self.authenticate()
        entries = (
            {"duration_minutes": 15, "uv_index": 3.0},
            {"duration_minutes": 30, "uv_index": 4.0},
        )

        total_minutes = 0
        total_vitamin_d = 0.0
        for entry in entries:
            total_minutes += entry["duration_minutes"]
            total_vitamin_d += estimate_vitamin_d(entry["duration_minutes"], entry["uv_index"])
            response = self.client.post(reverse("sun_exposure"), entry, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        summary_response = self.client.get(reverse("sun_exposure_summary"))
        self.assertEqual(summary_response.status_code, status.HTTP_200_OK)
        data = summary_response.data
        self.assertEqual(data["total_sessions"], len(entries))
        self.assertEqual(data["total_minutes"], total_minutes)
        self.assertAlmostEqual(data["total_vitamin_d"], round(total_vitamin_d, 2))
        self.assertIsNotNone(data["last_entry"])

    @patch("api.views.fetch_uv_index_data")
    @patch("api.views.resolve_coordinates")
    def test_smart_location_endpoint_uses_services(self, mock_resolve, mock_fetch):
        self.authenticate()
        mock_resolve.return_value = (40.0, -3.7)
        mock_fetch.return_value = {"result": {"uv": 6.5}}

        response = self.client.get(reverse("smart_location_uv_index"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["location"], {"latitude": 40.0, "longitude": -3.7})
        self.assertEqual(response.data["uv_data"], {"result": {"uv": 6.5}})

    @patch("api.views.resolve_coordinates", side_effect=LocationResolutionError("boom"))
    def test_smart_location_endpoint_handles_resolution_errors(self, mock_resolve):
        self.authenticate()
        response = self.client.get(reverse("smart_location_uv_index"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    @patch("api.views.resolve_coordinates", return_value=(0.0, 0.0))
    @patch("api.views.fetch_uv_index_data", side_effect=UVServiceError("service unavailable"))
    def test_smart_location_endpoint_handles_uv_service_errors(self, mock_fetch, mock_resolve):
        self.authenticate()
        response = self.client.get(reverse("smart_location_uv_index"))
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("error", response.data)
