from rest_framework import authentication, exceptions
from .auth0_jwt import verify_jwt

class Auth0JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header.split(" ")[1]
        try:
            payload = verify_jwt(token)
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Invalid JWT: {str(e)}")
        # `payload["sub"]` is usually the unique user id in Auth0
        user_id = payload.get("sub")
        if not user_id:
            raise exceptions.AuthenticationFailed("Token missing subject claim")
        # Optionally fetch or create a local Django user to represent this
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user, _ = User.objects.get_or_create(username=user_id, defaults={
            "email": payload.get("email", ""),
        })
        return (user, None)
