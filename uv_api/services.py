"""Integration helpers for fetching UV data with caching and fallbacks."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache

from .exceptions import UVServiceError

CACHE_TIMEOUT_SECONDS = 10 * 60  # cache each response for 10 minutes
TIME_BUCKET_MINUTES = 15


def _round_time_to_bucket(moment: datetime) -> datetime:
    minute = (moment.minute // TIME_BUCKET_MINUTES) * TIME_BUCKET_MINUTES
    return moment.replace(minute=minute, second=0, microsecond=0)


def _cache_key(lat: float, lon: float, bucket: datetime) -> str:
    return f"uv:{round(lat, 3)}:{round(lon, 3)}:{bucket.isoformat()}"


def _build_headers() -> dict[str, str]:
    api_key = getattr(settings, "UV_API_KEY", None) or getattr(settings, "OPENUV_API_KEY", "")
    headers = {"Accept": "application/json"}
    if api_key:
        headers["x-access-token"] = api_key
    return headers


def _parse_uv_payload(payload: dict[str, Any], moment: datetime) -> dict[str, Any]:
    result = payload.get("result") or payload.get("current") or {}
    if "uv" not in result:
        raise UVServiceError("UV value missing from response")

    uv_now = float(result.get("uv", 0.0))

    forecast_entries: list[dict[str, Any]] = []
    forecast_key = payload.get("forecast") or payload.get("uv_forecast") or []
    for item in forecast_key[:6]:  # limit to next few entries
        timestamp = item.get("uv_time") or item.get("timestamp")
        if not timestamp:
            continue
        try:
            when = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            continue
        forecast_entries.append(
            {
                "time": when.astimezone(timezone.utc).isoformat(),
                "uv_index": float(item.get("uv", item.get("uv_index", 0.0))),
            }
        )

    if not forecast_entries:
        # create a simple trend if API didn't return one
        for hours in range(1, 4):
            forecast_entries.append(
                {
                    "time": (moment + timedelta(hours=hours)).astimezone(timezone.utc).isoformat(),
                    "uv_index": max(uv_now - 0.5 * hours, 0.0),
                }
            )

    return {
        "uv_index_now": uv_now,
        "uv_forecast": forecast_entries,
        "data_quality": "normal",
    }


def _fallback_payload(moment: datetime) -> dict[str, Any]:
    # Provide a conservative assumption
    local_hour = moment.astimezone(timezone.utc).hour
    if 10 <= local_hour <= 15:
        uv_now = 8.0
    elif 7 <= local_hour < 10 or 15 < local_hour <= 17:
        uv_now = 5.0
    else:
        uv_now = 2.0

    trend = [
        {
            "time": (moment + timedelta(hours=i)).astimezone(timezone.utc).isoformat(),
            "uv_index": max(uv_now - 1.0 * i, 0.5),
        }
        for i in range(1, 4)
    ]
    return {
        "uv_index_now": uv_now,
        "uv_forecast": trend,
        "data_quality": "degraded",
        "message": "Using fallback UV data due to upstream service issues.",
    }


def get_uv_data(latitude: float, longitude: float, when: datetime | None = None) -> dict[str, Any]:
    """Return UV data for the given coordinates.

    The response is cached per 15-minute bucket. When the external API is
    unavailable, a conservative fallback is returned instead of raising.
    """

    if when is None:
        when = datetime.now(timezone.utc)

    bucket = _round_time_to_bucket(when.astimezone(timezone.utc))
    cache_key = _cache_key(latitude, longitude, bucket)
    cached = cache.get(cache_key)
    if cached:
        return {**cached, "cached": True}

    base_url = getattr(settings, "UV_API_BASE_URL", None) or getattr(
        settings,
        "OPENUV_URL_TEMPLATE",
        "https://api.openuv.io/api/v1/uv?lat={lat}&lng={lon}",
    )

    if "{" in base_url:
        url = base_url.format(lat=latitude, lon=longitude)
    else:
        url = base_url

    try:
        response = requests.get(url, headers=_build_headers(), timeout=5)
        response.raise_for_status()
        payload = response.json()
        parsed = _parse_uv_payload(payload, when)
    except (requests.RequestException, ValueError, UVServiceError, KeyError, Exception) as exc:
        parsed = _fallback_payload(when)
        parsed["error"] = str(exc)
    cache.set(cache_key, parsed, CACHE_TIMEOUT_SECONDS)
    return parsed
