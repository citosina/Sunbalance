from django.contrib.auth.models import User
from django.db import models


class SunExposure(models.Model):
    """Represents a single sun exposure tracking entry for a user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    duration_minutes = models.IntegerField()
    uv_index = models.FloatField()
    vitamin_d_produced = models.FloatField()  # Estimated amount in IU

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.duration_minutes} min"


