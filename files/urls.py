from django.urls import path
from .views import GetUploadURLView, ConfirmUploadView


urlpatterns = [
    path('upload/', GetUploadURLView.as_view(), name='upload'),
    path('upload/confirm/', ConfirmUploadView.as_view(), name='confirm-upload'),
]