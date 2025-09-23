from django.urls import path
from .views import GetUploadURLView, ConfirmUploadView, GetDownloadURLView, CreateSharedLinkView, AccessSharedLinkView


urlpatterns = [
    path(
        "upload/", GetUploadURLView.as_view(), name="upload"
    ),  # request presigned upload URL
    path(
        "upload/confirm/", ConfirmUploadView.as_view(), name="confirm-upload"
    ),  # confirm upload finished
    path(
        "download/", GetDownloadURLView.as_view(), name="download"
    ),  # request presigned download URL
    path(
        "share/create/", CreateSharedLinkView.as_view(), name="create-shared-link"
    ),  # create a shared link
    path(
        "share/access/<str:token>/", AccessSharedLinkView.as_view(), name="access-shared-link"
    ),  # access a shared link
]
