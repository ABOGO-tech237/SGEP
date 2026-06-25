from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsSuperAdmin

from .serializers import (
	AttendanceCreateSerializer,
	AttendanceSerializer,
	AttendanceStatsSerializer,
	AttendanceUpdateSerializer,
	JustifySerializer,
)
from .services import AttendanceService
from .tasks import generate_attendance_export_task


class AttendanceListCreateView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		records = AttendanceService.list(
			class_id=request.query_params.get("class_id"),
			student_id=request.query_params.get("student_id"),
			date_from=request.query_params.get("date_from"),
			date_to=request.query_params.get("date_to"),
		)
		serializer = AttendanceSerializer(records, many=True)
		return Response(serializer.data)

	def post(self, request):
		serializer = AttendanceCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		record = AttendanceService.record_absence(
			student_id=data["student_id"],
			class_id=data["class_id"],
			date_value=data["date"],
			absence_type=data["type"],
			motif=data.get("motif", ""),
			recorded_by=str(request.user.id),
			academic_year_id=data["academic_year_id"],
		)
		return Response(AttendanceSerializer(record).data, status=status.HTTP_201_CREATED)


class AttendanceDetailView(APIView):
	permission_classes = [IsSuperAdmin]

	def put(self, request, pk: str):
		serializer = AttendanceUpdateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		record = AttendanceService.update(pk, serializer.validated_data)
		return Response(AttendanceSerializer(record).data)


class AttendanceJustifyView(APIView):
	permission_classes = [IsSuperAdmin]

	def post(self, request, pk: str):
		serializer = JustifySerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		record = AttendanceService.justify(pk, serializer.validated_data["motif"])
		return Response(AttendanceSerializer(record).data)


class AttendanceStatsView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		class_id = request.query_params.get("class_id")
		date_from = request.query_params.get("date_from")
		date_to = request.query_params.get("date_to")

		if not class_id or not date_from or not date_to:
			return Response(
				{"detail": "class_id, date_from et date_to sont requis."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		stats = AttendanceService.get_stats(class_id, date_from, date_to)
		serializer = AttendanceStatsSerializer(stats, many=True)
		return Response(serializer.data)


class AttendanceExportView(APIView):
	permission_classes = [IsSuperAdmin]

	def get_format_suffix(self, **kwargs):
		return None

	def get(self, request):
		export_format = request.query_params.get("format", "excel")
		if export_format not in ("pdf", "excel"):
			return Response(
				{"detail": "Le format doit être 'pdf' ou 'excel'."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		params = dict(request.query_params)
		job = AttendanceService.create_export_job(export_format, str(request.user.id), params)
		generate_attendance_export_task.delay(job["id"], export_format, params)
		return Response({"job_id": job["id"]}, status=status.HTTP_202_ACCEPTED)
