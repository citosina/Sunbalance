from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class SunExposure(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    duration_minutes = models.IntegerField()
    uv_index = models.FloatField()
    vitamin_d_produced = models.FloatField()  # Estimated amount in IU

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.duration_minutes} min"


