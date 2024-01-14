from django.contrib.auth.models import AbstractUser
from django.db import models

from timezone_field import TimeZoneField


class User(AbstractUser):
    email = models.EmailField(blank=False, unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not hasattr(self, "profile"):
            Profile.objects.create(user=self)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tz = TimeZoneField(default="America/New_York", verbose_name="Timezone")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s profile"
