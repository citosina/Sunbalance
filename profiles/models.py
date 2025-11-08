"""Models that capture onboarding and profile data."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def default_time_windows() -> list[str]:
    return ["morning", "afternoon"]


def default_clothing_preferences() -> dict:
    return {
        "exposed_fraction": 0.35,  # 35% of body typically exposed
        "hats": True,
    }


class UserProfile(models.Model):
    """Global preferences for a user."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    default_latitude = models.FloatField(null=True, blank=True)
    default_longitude = models.FloatField(null=True, blank=True)
    default_altitude_m = models.IntegerField(default=0)
    default_skin_type = models.CharField(
        max_length=3,
        choices=[
            ("I", "Type I"),
            ("II", "Type II"),
            ("III", "Type III"),
            ("IV", "Type IV"),
            ("V", "Type V"),
            ("VI", "Type VI"),
        ],
        default="III",
    )
    preferred_time_windows = models.JSONField(default=default_time_windows)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"UserProfile<{self.user_id}>"


class SunProfile(models.Model):
    """Represents a person (user or dependent) for recommendations."""

    RELATIONSHIP_CHOICES = [
        ("self", "Self"),
        ("child", "Child"),
        ("toddler", "Toddler"),
        ("partner", "Partner"),
        ("other", "Other"),
    ]
    AGE_GROUP_CHOICES = [
        ("adult", "Adult"),
        ("child", "Child"),
        ("toddler", "Toddler"),
    ]
    SKIN_TYPE_CHOICES = [
        ("I", "Fitzpatrick I"),
        ("II", "Fitzpatrick II"),
        ("III", "Fitzpatrick III"),
        ("IV", "Fitzpatrick IV"),
        ("V", "Fitzpatrick V"),
        ("VI", "Fitzpatrick VI"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sun_profiles")
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=32, choices=RELATIONSHIP_CHOICES)
    age_group = models.CharField(max_length=32, choices=AGE_GROUP_CHOICES)
    skin_type = models.CharField(max_length=3, choices=SKIN_TYPE_CHOICES)
    preferred_time_windows = models.JSONField(default=default_time_windows)
    clothing_preferences = models.JSONField(default=default_clothing_preferences)
    sunscreen_spf = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(5), MaxValueValidator(100)],
    )
    hats = models.BooleanField(default=True)
    location_latitude = models.FloatField(null=True, blank=True)
    location_longitude = models.FloatField(null=True, blank=True)
    altitude_m = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["user", "name"]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"SunProfile<{self.name}>"
