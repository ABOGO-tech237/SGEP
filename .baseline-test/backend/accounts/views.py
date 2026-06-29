import importlib

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
	ChangePasswordSerializer,
	LoginSerializer,
	LogoutSerializer,
	RefreshSerializer,
)
from accounts.services import AdminDashboardService, AuthService
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
