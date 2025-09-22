from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializers import UserProfileSerializer


class MyProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        return Response({
            "user_id": request.user.username,
            "email": request.user.email,
        })


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        auth0_id = request.user.sub
        # sub is an attribute of the authenticated user object, typically set by Auth0. It represents the unique identifier for the user in Auth0. This value is used to look up the corresponding user profile in your database.

        profile = UserProfile.objects.get(auth0_id=auth0_id)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
