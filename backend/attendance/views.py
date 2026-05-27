from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse

from accounts.permissions import IsSuperAdmin
from attendance.serializers import (
	AttendanceCreateSerializer,
	AttendanceExportQuerySerializer,
	AttendanceJustifySerializer,
	AttendanceQuerySerializer,
	AttendanceSerializer,
	AttendanceStatsQuerySerializer,
	AttendanceUpdateSerializer,
)
from attendance.swagger import build_attendance_openapi_schema
from attendance.services import AttendanceService


class AttendanceListCreateView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		serializer = AttendanceQuerySerializer(data=request.query_params)
		serializer.is_valid(raise_exception=True)
		params = serializer.validated_data
		payload = AttendanceService.list(
			class_id=params.get("class_id"),
			student_id=params.get("student_id"),
			date_from=str(params.get("date_from")) if params.get("date_from") else None,
			date_to=str(params.get("date_to")) if params.get("date_to") else None,
		)
		out = AttendanceSerializer(payload["results"], many=True)
		return Response({"count": payload["count"], "results": out.data}, status=status.HTTP_200_OK)

	def post(self, request):
		serializer = AttendanceCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		created = AttendanceService.record_absence(
			student_id=data["student_id"],
			class_id=data["class_id"],
			date=str(data["date"]),
			absence_type=data["type"],
			motif=data.get("motif"),
		)
		return Response(AttendanceSerializer(created).data, status=status.HTTP_201_CREATED)


class AttendanceDetailView(APIView):
	permission_classes = [IsSuperAdmin]

	def put(self, request, record_id: str):
		serializer = AttendanceUpdateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = dict(serializer.validated_data)
		if "date" in data:
			data["date"] = str(data["date"])
		updated = AttendanceService.update(record_id, data)
		return Response(AttendanceSerializer(updated).data, status=status.HTTP_200_OK)


class AttendanceJustifyView(APIView):
	permission_classes = [IsSuperAdmin]

	def post(self, request, record_id: str):
		serializer = AttendanceJustifySerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		updated = AttendanceService.justify(
			record_id=record_id,
			motif=data["motif"],
			justification_doc=data.get("justification_doc"),
		)
		return Response(AttendanceSerializer(updated).data, status=status.HTTP_200_OK)


class AttendanceStatsView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		serializer = AttendanceStatsQuerySerializer(data=request.query_params)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		payload = AttendanceService.get_stats(
			class_id=data["class_id"],
			date_from=str(data["date_from"]),
			date_to=str(data["date_to"]),
		)
		return Response(payload, status=status.HTTP_200_OK)


class AttendanceExportView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		serializer = AttendanceExportQuerySerializer(data=request.query_params)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		job_id = AttendanceService.export(
			class_id=data["class_id"],
			date_from=str(data["date_from"]),
			date_to=str(data["date_to"]),
			export_format=data["format"],
			requested_by=str(request.user.id),
		)
		return Response({"job_id": job_id}, status=status.HTTP_202_ACCEPTED)


class AttendanceSwaggerView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		return Response(build_attendance_openapi_schema(), status=status.HTTP_200_OK)


class AttendanceSwaggerUIView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		spec_url = request.build_absolute_uri("/api/v1/attendance/swagger/")
		html = """
<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1" />
		<title>SGEP Attendance API — Swagger UI</title>
		<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4.18.3/swagger-ui.css" />
	</head>
	<body>
		<div id="swagger-ui"></div>
		<script src="https://unpkg.com/swagger-ui-dist@4.18.3/swagger-ui-bundle.js"></script>
		<script>
			SwaggerUIBundle({
				url: '__SPEC_URL__',
				dom_id: '#swagger-ui',
				presets: [SwaggerUIBundle.presets.apis],
			})
		</script>
	</body>
</html>
"""
		html = html.replace("__SPEC_URL__", spec_url)
		return HttpResponse(html)
