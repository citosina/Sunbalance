"""Core recommendation heuristics for sun exposure."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

BASE_MED_MINUTES = {
    "I": 60,
    "II": 75,
    "III": 100,
    "IV": 150,
    "V": 200,
    "VI": 240,
}

AGE_ADJUSTMENTS = {
    "adult": 1.0,
    "child": 0.7,
    "toddler": 0.5,
}

SAFETY_FACTOR = 0.6  # Always stay safely below the expected MED
ALTITUDE_DECREMENT_PER_1000M = 0.12  # roughly 12% more UV dose per 1000 m
CLOUD_REDUCTION = {
    "heavy": 0.4,
    "medium": 0.65,
    "light": 0.8,
}


@dataclass
class Recommendation:
    status: str
    recommended_minutes_min: int
    recommended_minutes_max: int
    warnings: List[str]
    suggested_windows: List[str]

    def as_dict(self) -> Dict[str, Any]:
        payload = {
            "status": self.status,
            "recommended_minutes_min": self.recommended_minutes_min,
            "recommended_minutes_max": self.recommended_minutes_max,
            "warnings": self.warnings,
        }
        if self.suggested_windows:
            payload["suggested_windows"] = self.suggested_windows
        return payload


def _apply_cloud_adjustment(uv_index: float, cloud_cover: float | None) -> float:
    if cloud_cover is None:
        return uv_index
    if cloud_cover >= 0.8:
        factor = CLOUD_REDUCTION["heavy"]
    elif cloud_cover >= 0.5:
        factor = CLOUD_REDUCTION["medium"]
    elif cloud_cover >= 0.2:
        factor = CLOUD_REDUCTION["light"]
    else:
        factor = 1.0
    return max(uv_index * factor, 0.1)


def _sunscreen_effective_uv(uv_index: float, sunscreen_spf: int | None) -> float:
    if not sunscreen_spf:
        return uv_index
    # Sunscreen is never perfect; we assume 40% reduction at SPF 30 and cap at 60%
    reduction = min(0.02 * sunscreen_spf, 0.6)
    return max(uv_index * (1 - reduction), 0.5)


def _clothing_factor(clothing_coverage: dict[str, Any], hats: bool) -> float:
    exposed_fraction = float(clothing_coverage.get("exposed_fraction", 0.35))
    exposed_fraction = max(0.0, min(exposed_fraction, 1.0))
    factor = max(0.35, 1 - exposed_fraction * 0.6)
    if not hats:
        factor *= 0.9
    return factor


def compute_recommendation(
    uv_index: float,
    skin_type: str,
    age_group: str,
    altitude_m: int,
    clothing_coverage: dict[str, Any] | None,
    sunscreen_spf: int | None,
    cloud_cover: float | None = None,
) -> dict[str, Any]:
    """Return a conservative recommendation dict.

    The heuristics intentionally err on the side of shorter exposure windows.
    """

    uv_index = max(uv_index, 0.1)
    raw_uv = uv_index
    adjusted_uv = _apply_cloud_adjustment(uv_index, cloud_cover)
    adjusted_uv = _sunscreen_effective_uv(adjusted_uv, sunscreen_spf)

    base_med = BASE_MED_MINUTES.get(skin_type, BASE_MED_MINUTES["III"])
    age_factor = AGE_ADJUSTMENTS.get(age_group, 0.7)
    altitude_penalty = 1 - min((altitude_m / 1000.0) * ALTITUDE_DECREMENT_PER_1000M, 0.45)
    coverage = clothing_coverage or {}
    hats = bool(coverage.get("hats", True)) if isinstance(coverage, dict) else True
    clothing_factor = _clothing_factor(coverage if isinstance(coverage, dict) else {}, hats)

    effective_minutes_to_med = base_med / adjusted_uv
    conservative_minutes = (
        effective_minutes_to_med * age_factor * altitude_penalty * clothing_factor * SAFETY_FACTOR
    )
    conservative_minutes = max(conservative_minutes, 3.0)
    recommended_max = min(conservative_minutes, 45.0)
    recommended_min = max(recommended_max * 0.6, 2.0)

    status = "good_now"
    warnings: list[str] = []
    suggested_windows: list[str] = []

    if raw_uv >= 9 or adjusted_uv >= 8:
        status = "avoid_now"
        warnings.append("UV is extreme. Stay indoors or find shade.")
        suggested_windows = ["early_morning", "late_afternoon"]
        recommended_max = min(recommended_max, 10)
        recommended_min = min(recommended_min, 5)
    elif raw_uv >= 7 or adjusted_uv >= 6:
        status = "caution_now"
        warnings.append("High UV – limit direct exposure and wear protection.")
        suggested_windows = ["morning", "late_afternoon"]
        recommended_max = min(recommended_max, 20)
        recommended_min = min(recommended_min, 8)
    elif adjusted_uv <= 2:
        status = "low_uv"
        warnings.append("UV is low. Consider gentle outdoor time but keep layers for warmth if needed.")

    if age_group in {"child", "toddler"}:
        warnings.append("Extra caution for young skin. Reapply sunscreen and monitor closely.")

    return Recommendation(
        status=status,
        recommended_minutes_min=int(round(recommended_min)),
        recommended_minutes_max=int(round(recommended_max)),
        warnings=warnings,
        suggested_windows=suggested_windows,
    ).as_dict()
