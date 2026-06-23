import importlib
import secrets

from django.conf import settings
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from appwrite.query import Query

try:
	ratelimit = importlib.import_module("django_ratelimit.decorators").ratelimit
except ModuleNotFoundError:  # pragma: no cover
	def ratelimit(*args, **kwargs):
		def _decorator(view_func):
			return view_func

		return _decorator

from accounts.serializers import (
	AdminDashboardSerializer,
	BootstrapSerializer,
	ChangePasswordSerializer,
	LoginSerializer,
	LogoutSerializer,
	RefreshSerializer,
)
from accounts.services import AdminDashboardService, AuthService
from accounts.login_user_service import create_or_reset_login_user
from accounts.repository import UserRepository
from accounts.permissions import IsSuperAdmin

@method_decorator(ratelimit(key="ip", rate="5/10m", method="POST", block=True), name="post")
class LoginView(APIView):
	authentication_classes: list = []
	permission_classes: list = []

	def post(self, request):
		serializer = LoginSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		tokens = AuthService.login(
			email=serializer.validated_data["email"],
			password=serializer.validated_data["password"],
		)
		return Response(tokens, status=status.HTTP_200_OK)


@method_decorator(ratelimit(key="ip", rate="3/h", method="POST", block=True), name="post")
class BootstrapView(APIView):
	"""One-time admin bootstrap when shell access is unavailable (e.g. Render free tier)."""

	authentication_classes: list = []
	permission_classes: list = []

	def post(self, request):
		secret = settings.BOOTSTRAP_SECRET
		if not secret:
			return Response(status=status.HTTP_404_NOT_FOUND)

		token = request.headers.get("X-Bootstrap-Token", "")
		if not secrets.compare_digest(token, secret):
			return Response(
				{"detail": "Token bootstrap invalide."},
				status=status.HTTP_403_FORBIDDEN,
			)

		if UserRepository.count() > 0 and "email" not in request.data:
			return Response(
				{
					"detail": (
						"Des utilisateurs existent déjà. "
						"Fournissez un email explicite pour créer ou réinitialiser un compte."
					)
				},
				status=status.HTTP_409_CONFLICT,
			)

		serializer = BootstrapSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		try:
			result = create_or_reset_login_user(**serializer.validated_data)
		except Exception as exc:
			return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		http_status = (
			status.HTTP_201_CREATED if result["action"] == "created" else status.HTTP_200_OK
		)
		return Response(result, status=http_status)


class RefreshTokenView(APIView):
	authentication_classes: list = []
	permission_classes: list = []

	def post(self, request):
		serializer = RefreshSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		payload = AuthService.refresh_access_token(
			refresh_token=serializer.validated_data["refresh"],
		)
		return Response(payload, status=status.HTTP_200_OK)


class LogoutView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		serializer = LogoutSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		AuthService.logout(refresh_token=serializer.validated_data["refresh"])
		return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		serializer = ChangePasswordSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		AuthService.change_password(
			user_id=str(request.user.id),
			old_password=serializer.validated_data["old_password"],
			new_password=serializer.validated_data["new_password"],
		)
		return Response({"detail": "Mot de passe modifie."}, status=status.HTTP_200_OK)


class AdminDashboardView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		payload = AdminDashboardService.get_overview()
		serializer = AdminDashboardSerializer(data=payload)
		serializer.is_valid(raise_exception=True)
		return Response(serializer.validated_data, status=status.HTTP_200_OK)
