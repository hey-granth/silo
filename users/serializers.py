from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id",
            "auth0_id",
            "plan",
            "email",
            "name",
            "bio",
            "created_at",
            "updated_at",
            "storage_used",
        ]
        read_only_fields = fields
