from django.db import models
from config import Config


# this is a local mirror to what data is stored in auth0
# we store auth0_id to link to the auth0 user
class UserProfile(models.Model):
    auth0_id = models.CharField(max_length=100, unique=True, db_index=True)
    plan = models.CharField(max_length=20, default="free", choices=Config.PLAN_CHOICES)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    storage_used = models.BigIntegerField(default=0)  # in bytes

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "User Profile"

    verbose_name_plural = "User Profiles"
