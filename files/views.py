import uuid
from django.utils.timezone import now
from config import Config
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from users.models import UserProfile
from .models import File, FileAccessLog
from .serializers import FileUploadConfirmSerializer, FileUploadRequestSerializer


# returns presigned URL for uploading a file
class GetUploadURLView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FileUploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Create file record (not marked uploaded yet)
        file_obj = File.objects.create(
            id=uuid.uuid4(),
            owner_id=request.user,  # mapped to UserProfile
            file_name=data['file_name'],
            file_size=data['file_size'],
            checksum=data['checksum'],
            file_path=f"uploads/{request.user.id}/{uuid.uuid4()}_{data['file_name']}",
        )

        # Generate presigned PUT URL (MinIO / S3 compatible)
        s3_client = Config.s3_client
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": Config.MINIO_BUCKET_NAME,
                "Key": file_obj.file_path,
                "ContentType": data['file_type'],
            },
            ExpiresIn=3600,
        )

        return Response({
            "file_id": str(file_obj.id),
            "upload_url": presigned_url,
            "file_path": file_obj.file_path,
        })



class ConfirmUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file_id = request.data.get("file_id")
        try:
            file_obj = File.objects.get(id=file_id, owner_id=request.user)
        except File.DoesNotExist:
            return Response({"detail": "File not found"}, status=404)

        # Mark file uploaded
        file_obj.uploaded = True
        file_obj.save(update_fields=["uploaded"])

        # Update user storage usage
        user_profile = UserProfile.objects.get(id=request.user.id)
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