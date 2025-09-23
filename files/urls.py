from django.urls import path
from .views import GetUploadURLView, ConfirmUploadView, GetDownloadURLView


urlpatterns = [
    path("upload/", GetUploadURLView.as_view(), name="upload"),     # request presigned upload URL
    path("upload/confirm/", ConfirmUploadView.as_view(), name="confirm-upload"),    # confirm upload finished
    path("download/", GetDownloadURLView.as_view(), name="download"),   # request presigned download URL
]
