from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsSuperAdmin

from .admin_dashboard_service import AdminDashboardService
from .school_services import AcademicYearService, LevelService, SchoolService
from .serializers import (
	AcademicYearSerializer,
	AdminDashboardResponseSerializer,
	LevelSerializer,
	SchoolSerializer,
)


class SchoolListCreateView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		return Response(SchoolSerializer(SchoolService.list(), many=True).data)

	def post(self, request):
		serializer = SchoolSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		school = SchoolService.create(serializer.validated_data)
		return Response(SchoolSerializer(school).data, status=status.HTTP_201_CREATED)


class SchoolDetailView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request, pk: str):
		return Response(SchoolSerializer(SchoolService.get(pk)).data)

	def patch(self, request, pk: str):
		serializer = SchoolSerializer(data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		school = SchoolService.update(pk, serializer.validated_data)
		return Response(SchoolSerializer(school).data)


class LevelListView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		return Response(LevelSerializer(LevelService.list(), many=True).data)


class AcademicYearListCreateView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		years = AcademicYearService.list(school_id=request.query_params.get("school_id"))
		return Response(AcademicYearSerializer(years, many=True).data)

	def post(self, request):
		serializer = AcademicYearSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		year = AcademicYearService.create(serializer.validated_data)
		return Response(AcademicYearSerializer(year).data, status=status.HTTP_201_CREATED)


class AcademicYearDetailView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request, pk: str):
		return Response(AcademicYearSerializer(AcademicYearService.get(pk)).data)

	def patch(self, request, pk: str):
		serializer = AcademicYearSerializer(data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		year = AcademicYearService.update(pk, serializer.validated_data)
		return Response(AcademicYearSerializer(year).data)


class AdminDashboardView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		dashboard = AdminDashboardService.build()
		return Response(AdminDashboardResponseSerializer(dashboard).data)
