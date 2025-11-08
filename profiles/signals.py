"""Signals for automatic profile creation."""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import SunProfile, UserProfile


User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance: User, created: bool, **kwargs):
    if not created:
        return

    user_profile = UserProfile.objects.create(user=instance)
    SunProfile.objects.create(
        user=instance,
        name=instance.username or "Me",
        relationship="self",
        age_group="adult",
        skin_type=user_profile.default_skin_type,
        is_primary=True,
    )
