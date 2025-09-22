from django.urls import path
from .views import GetUploadURLView, ConfirmUploadView, GetDownloadURLView


urlpatterns = [
    path('upload/', GetUploadURLView.as_view(), name='upload'),
    path('upload/confirm/', ConfirmUploadView.as_view(), name='confirm-upload'),
    path('download/', GetDownloadURLView.as_view(), name='download'),
]