"""Tests for the UV API integration helpers."""

from datetime import datetime, timezone
from unittest import mock

from django.core.cache import cache
from django.test import TestCase

from .services import get_uv_data


class UVServiceTests(TestCase):
    def setUp(self):
        cache.clear()

    @mock.patch("uv_api.services.requests.get")
    def test_get_uv_data_returns_parsed_payload(self, mock_get):
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "result": {"uv": 5.2},
            "forecast": [
                {"uv_time": "2024-01-01T10:00:00Z", "uv": 4.8},
                {"uv_time": "2024-01-01T11:00:00Z", "uv": 6.0},
            ],
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        data = get_uv_data(19.4326, -99.1332, datetime.now(timezone.utc))
        self.assertEqual(data["data_quality"], "normal")
        self.assertEqual(data["uv_index_now"], 5.2)
        self.assertEqual(len(data["uv_forecast"]), 2)

    @mock.patch("uv_api.services.requests.get")
    def test_fallback_is_used_on_failure(self, mock_get):
        mock_get.side_effect = Exception("timeout")
        data = get_uv_data(19.4326, -99.1332, datetime.now(timezone.utc))
        self.assertEqual(data["data_quality"], "degraded")
        self.assertIn("message", data)
