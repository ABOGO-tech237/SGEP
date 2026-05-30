from __future__ import annotations

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from accounts.models import User
from accounts.repository import UserRepository


class AppwriteJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        # Support different SimpleJWT versions: prefer the configured claim
        # attribute when available, otherwise fall back to common claims.
        if hasattr(self, "user_id_claim") and self.user_id_claim:
            user_id = validated_token.get(self.user_id_claim)
        else:
            user_id = validated_token.get("user_id") or validated_token.get("sub")

        if not user_id:
            raise InvalidToken("Token sans user_id.")

        user_payload = UserRepository.get_by_id(str(user_id))
        if not user_payload:
            raise InvalidToken("Utilisateur introuvable.")

        return User.from_appwrite(user_payload)
