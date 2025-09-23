import hashlib
import secrets
import uuid
from django.utils.timezone import now
from config import Config
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from users.models import UserProfile
from .models import File, FileAccessLog, SharedFileLink
from .serializers import (
    FileUploadConfirmSerializer,
    FileUploadRequestSerializer,
    FileDownloadResponseSerializer,
    FileDownloadRequestSerializer,
    SharedLinkResponseSerializer,
    CreateSharedLinkSerializer,
)


# returns presigned URL for uploading a file
class GetUploadURLView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        serializer = FileUploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Create file record (not marked uploaded yet)
        file_obj: File = File.objects.create(
            id=uuid.uuid4(),
            owner_id=request.user,  # mapped to UserProfile
            file_name=data["file_name"],
            file_size=data["file_size"],
            checksum=data["checksum"],
            file_path=f"uploads/{request.user.id}/{uuid.uuid4()}_{data['file_name']}",
        )

        # Generate presigned PUT URL (MinIO)
        presigned_url: str = Config.s3_client.presigned_put_object(
            Config.MINIO_BUCKET_NAME,
            file_obj.file_path,
            expires=3600,
        )

        return Response(
            {
                "file_id": str(file_obj.id),
                "upload_url": presigned_url,
                "file_path": file_obj.file_path,
            }
        )


# After uploading the file to the presigned URL, the client calls this to confirm upload
class ConfirmUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        file_id = request.data.get("file_id")
        try:
            file_obj: File = File.objects.get(id=file_id, owner_id=request.user)
        except File.DoesNotExist:
            return Response({"detail": "File not found"}, status=404)

        # Mark file uploaded
        file_obj.uploaded = True
        file_obj.save(update_fields=["uploaded"])

        # Update user storage usage
        user_profile: UserProfile = UserProfile.objects.get(id=request.user.id)
        user_profile.storage_used += file_obj.file_size
        user_profile.save(update_fields=["storage_used"])

        # Log upload action
        FileAccessLog.objects.create(
            file_id=file_obj,
            user_id=request.user,
            action="UPLOAD",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            timestamp=now(),
        )

        return Response(FileUploadConfirmSerializer(file_obj).data)


# returns presigned URL for downloading a file
class GetDownloadURLView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        serializer = FileDownloadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_id = serializer.validated_data["file_id"]

        try:
            file_obj: File = File.objects.get(
                id=file_id, owner_id=request.user, uploaded=True
            )
        except File.DoesNotExist:
            return Response({"detail": "File not found"}, status=404)

        # Generate presigned GET URL (MinIO)
        presigned_url: str = Config.s3_client.presigned_get_object(
            Config.MINIO_BUCKET_NAME,
            file_obj.file_path,
            expires=3600,
        )

        # Log download
        FileAccessLog.objects.create(
            file_id=file_obj,
            user_id=request.user,
            action="DOWNLOAD",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            timestamp=now(),
        )

        response_data: dict[str, str | int] = {
            "download_url": presigned_url,
            "file_name": file_obj.file_name,
            "file_size": file_obj.file_size,
        }
        return Response(FileDownloadResponseSerializer(response_data).data)


class CreateSharedLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        serializer = CreateSharedLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            file_obj: File = File.objects.get(
                id=data["file_id"], owner_id=request.user, uploaded=True
            )
        except File.DoesNotExist:
            return Response({"detail": "File not found"}, status=404)

        token: str = secrets.token_urlsafe(
            32
        )  # Return a random URL-safe text string, in Base64 encoding.
        password_hash: str = (
            hashlib.sha256(data["password"].encode()).hexdigest()
            if data.get("password")
            else None
        )

        shared_link: SharedFileLink = SharedFileLink.objects.create(
            id=uuid.uuid4(),
            owner=request.user,
            file_id=file_obj,
            token=token,
            expires_at=data.get("expires_at"),
            max_downloads=data.get("max_downloads"),
            permission=data["permission"],
            password_hash=password_hash,
        )

        return Response(SharedLinkResponseSerializer(shared_link).data)


class AccessSharedLinkView(APIView):
    def post(self, request) -> Response:
        token: str = request.data.get("token")
        password: str = request.data.get("password")

        try:
            shared_link: SharedFileLink = SharedFileLink.objects.select_related(
                "file_id"
            ).get(token=token)
        except SharedFileLink.DoesNotExist:
            return Response({"detail": "Invalid link"}, status=404)

        # Check expiry
        if shared_link.expires_at and shared_link.expires_at < now():
            return Response({"detail": "Link expired"}, status=403)

        # Check max downloads
        if (
            shared_link.max_downloads
            and shared_link.download_count >= shared_link.max_downloads
        ):
            return Response({"detail": "Download limit reached"}, status=403)

        # Check password
        if shared_link.password_hash:
            if (
                not password
                or hashlib.sha256(password.encode()).hexdigest()
                != shared_link.password_hash
            ):
                return Response({"detail": "Invalid password"}, status=403)

        # Generate presigned GET URL
        file_obj = shared_link.file_id
        presigned_url: str = Config.s3_client.presigned_get_object(
            Config.MINIO_BUCKET_NAME,
            file_obj.file_path,
            expires=3600,
        )

        # Update counters
        shared_link.download_count += 1
        shared_link.save(update_fields=["download_count"])

        FileAccessLog.objects.create(
            file_id=file_obj,
            user_id=shared_link.owner,  # link owner is logged
            action="SHARE",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return Response({"download_url": presigned_url})
