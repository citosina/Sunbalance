"""Utility services that power the SunBalance API."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import requests
from django.conf import settings


class LocationResolutionError(Exception):
    """Raised when the application is unable to determine the user location."""


class UVServiceError(Exception):
    """Raised when fetching data from the OpenUV service fails."""


def resolve_coordinates(
    latitude: Optional[str] = None,
    longitude: Optional[str] = None,
    *,
    session: requests.sessions.Session | Any = requests,
) -> Tuple[float, float]:
    """Resolve a pair of coordinates.

    If coordinates are supplied they are validated, otherwise an IP geolocation
    service is queried. The default IP service can be overridden with the
    ``IP_GEOLOCATION_URL`` setting.
    """

    if latitude is not None and longitude is not None:
        try:
            return float(latitude), float(longitude)
        except (TypeError, ValueError) as exc:
            raise LocationResolutionError("Invalid latitude or longitude provided.") from exc

    geolocation_url = getattr(settings, "IP_GEOLOCATION_URL", "https://ipapi.co/json/")

    try:
        response = session.get(geolocation_url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise LocationResolutionError("Unable to determine location from IP.") from exc

    data = response.json()
    lat = data.get("latitude") or data.get("lat")
    lon = data.get("longitude") or data.get("lon") or data.get("lng")

    if lat is None or lon is None:
        raise LocationResolutionError("Geolocation service did not return coordinates.")

    try:
        return float(lat), float(lon)
    except (TypeError, ValueError) as exc:
        raise LocationResolutionError("Geolocation service returned invalid coordinates.") from exc


def fetch_uv_index_data(
    latitude: float,
    longitude: float,
    *,
    api_key: Optional[str] = None,
    session: requests.sessions.Session | Any = requests,
) -> Dict[str, Any]:
    """Fetch UV index data from the OpenUV API."""

    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError) as exc:
        raise UVServiceError("Invalid coordinates for UV lookup.") from exc

    api_key = api_key or getattr(settings, "OPENUV_API_KEY", "")
    if not api_key:
        raise UVServiceError("OpenUV API key is not configured.")

    url_template = getattr(
        settings, "OPENUV_URL_TEMPLATE", "https://api.openuv.io/api/v1/uv?lat={lat}&lng={lon}"
    )
    url = url_template.format(lat=lat, lon=lon)

    headers = {"x-access-token": api_key}

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = getattr(exc.response, "status_code", None)
        raise UVServiceError(
            f"OpenUV service returned status code {status_code or 'unknown'}."
        ) from exc
    except requests.RequestException as exc:
        raise UVServiceError("Unable to contact the OpenUV service.") from exc

    return response.json()


def estimate_vitamin_d(duration_minutes: int, uv_index: float) -> float:
    """Estimate vitamin D production based on duration and UV index."""

    if duration_minutes <= 0 or uv_index <= 0:
        return 0.0

    baseline_minutes = getattr(settings, "VITAMIN_D_BASELINE_MINUTES", 15)
    baseline_uv = getattr(settings, "VITAMIN_D_BASELINE_UV_INDEX", 3.0)

    vitamin_d = (uv_index / baseline_uv) * (duration_minutes / baseline_minutes) * 1000

    return round(vitamin_d, 2)


__all__ = [
    "LocationResolutionError",
    "UVServiceError",
    "resolve_coordinates",
    "fetch_uv_index_data",
    "estimate_vitamin_d",
]
