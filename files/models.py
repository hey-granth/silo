from django.db import models
from users.models import UserProfile
from config import Config


class File(models.Model):
    id = models.UUIDField(primary_key=True)
    owner_id = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="files", db_index=True
    )
    file_path = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # in bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded = models.BooleanField(default=False)
    # to avoid duplicate uploads
    checksum = models.CharField(max_length=64, db_index=True)  # SHA-256 checksum
    file_type = models.CharField(
        max_length=50, null=True, blank=True, choices=Config.FILE_TYPE_CHOICES
    )  # MIME type

    def __str__(self):
        return f"{self.file_name} ({self.file_size} bytes)"


# for bigger files
class FileChunk(models.Model):
    id = models.UUIDField(primary_key=True)
    file_id = models.ForeignKey(
        File, on_delete=models.CASCADE, related_name="chunks", db_index=True
    )
    chunk_index = models.IntegerField()  # index of the chunk
    chunk_size = models.BigIntegerField()  # in bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)
    checksum = models.CharField(max_length=64)  # SHA-256 checksum of the chunk
    storage_path = models.CharField(max_length=255)  # path in storage backend
    uploaded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chunk {self.chunk_index} of {self.file_id}"

    class Meta:
        unique_together = ("file_id", "chunk_index")


class FileAccessLog(models.Model):
    id = models.AutoField(primary_key=True)
    file_id = models.ForeignKey(
        File, on_delete=models.CASCADE, related_name="access_logs", db_index=True
    )
    user_id = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="file_access_logs",
        db_index=True,
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    action = models.enums.TextChoices("Action", "UPLOAD DOWNLOAD DELETE SHARE")
    timestamp = models.DateTimeField(auto_now_add=True)
    token = models.CharField(
        max_length=255, null=True, blank=True
    )  # for sharing via token links

    def __str__(self):
        return f"{self.user_id} {self.action} {self.file_id} at {self.timestamp}"


class SharedFileLink(models.Model):
    id = models.UUIDField(primary_key=True)
    owner = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="shared_links",
        db_index=True,
    )
    file_id = models.ForeignKey(
        File, on_delete=models.CASCADE, related_name="shared_links", db_index=True
    )
    token = models.CharField(
        max_length=255, unique=True, db_index=True
    )  # unique token for sharing
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # null means never expires
    max_downloads = models.IntegerField(null=True, blank=True)  # null means unlimited
    download_count = models.IntegerField(default=0)
    permission = models.enums.TextChoices("Permission", "DOWNLOAD VIEW")
    password_hash = models.CharField(
        max_length=255, null=True, blank=True
    )  # to make it password protected

    def __str__(self):
        return f"Shared link for {self.file_id} by {self.owner}"
