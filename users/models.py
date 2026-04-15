from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .constants import (
    ACCESS_LEVEL_ADMIN,
    ACCESS_LEVEL_CHOICES,
    DEFAULT_ACCESS_LEVEL,
    DEFAULT_GROUP_TYPE,
    GROUP_TYPE_ADMIN,
    GROUP_TYPE_CHOICES,
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    group_type = models.CharField(
        max_length=32,
        choices=GROUP_TYPE_CHOICES,
        default=DEFAULT_GROUP_TYPE,
    )
    access_level = models.CharField(
        max_length=16,
        choices=ACCESS_LEVEL_CHOICES,
        default=DEFAULT_ACCESS_LEVEL,
    )

    def clean(self):
        super().clean()

        if self.group_type == GROUP_TYPE_ADMIN and self.access_level != ACCESS_LEVEL_ADMIN:
            raise ValidationError(
                {
                    "access_level": "Admin group type requires admin access level.",
                }
            )

        if self.group_type != GROUP_TYPE_ADMIN and self.access_level == ACCESS_LEVEL_ADMIN:
            raise ValidationError(
                {
                    "access_level": "Only admin group type can have admin access level.",
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} profile"
