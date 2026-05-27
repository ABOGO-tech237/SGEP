from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsSuperAdmin
from students.serializers import (
	StudentCreateSerializer,
	StudentEnrollSerializer,
	StudentListSerializer,
	StudentQuerySerializer,
	StudentPromoteSerializer,
	StudentSerializer,
)
from students.swagger import build_student_openapi_schema
from students.services import StudentService
from django.http import HttpResponse


class StudentListView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		serializer = StudentQuerySerializer(data=request.query_params)
		serializer.is_valid(raise_exception=True)
		payload = StudentService.list(**serializer.validated_data)
		serializer = StudentListSerializer(payload["results"], many=True)
		return Response(
			{
				"count": payload["count"],
				"page": payload["page"],
				"page_size": payload["page_size"],
				"results": serializer.data,
			},
			status=status.HTTP_200_OK,
		)

	def post(self, request):
		serializer = StudentCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		student = StudentService.create(serializer.validated_data)
		return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)


class StudentDetailView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request, student_id: str):
		student = StudentService.get(student_id)
		return Response(StudentSerializer(student).data, status=status.HTTP_200_OK)

	def patch(self, request, student_id: str):
		serializer = StudentCreateSerializer(
			data=request.data,
			partial=True,
			context={"student_id": student_id},
		)
		serializer.is_valid(raise_exception=True)
		student = StudentService.update(student_id, serializer.validated_data)
		return Response(StudentSerializer(student).data, status=status.HTTP_200_OK)

	def delete(self, request, student_id: str):
		StudentService.soft_delete(student_id)
		return Response(status=status.HTTP_204_NO_CONTENT)


class StudentHistoryView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request, student_id: str):
		history = StudentService.get_history(student_id)
		return Response(history, status=status.HTTP_200_OK)


class StudentEnrollView(APIView):
	permission_classes = [IsSuperAdmin]

	def post(self, request, student_id: str):
		serializer = StudentEnrollSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		student = StudentService.enroll(
			student_id=student_id,
			class_id=serializer.validated_data["class_id"],
			academic_year_id=serializer.validated_data["academic_year_id"],
		)
		return Response(StudentSerializer(student).data, status=status.HTTP_200_OK)


class StudentPromoteView(APIView):
	permission_classes = [IsSuperAdmin]

	def post(self, request, student_id: str):
		serializer = StudentPromoteSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		student = StudentService.promote(
			student_id=student_id,
			target_class_id=serializer.validated_data["target_class_id"],
		)
		return Response(StudentSerializer(student).data, status=status.HTTP_200_OK)


class StudentExportPdfView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		serializer = StudentQuerySerializer(data=request.query_params)
		serializer.is_valid(raise_exception=True)
		job_id = StudentService.export_pdf(serializer.validated_data, str(request.user.id))
		return Response({"job_id": job_id}, status=status.HTTP_202_ACCEPTED)


class StudentExportExcelView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		serializer = StudentQuerySerializer(data=request.query_params)
		serializer.is_valid(raise_exception=True)
		job_id = StudentService.export_excel(serializer.validated_data, str(request.user.id))
		return Response({"job_id": job_id}, status=status.HTTP_202_ACCEPTED)


class StudentSwaggerView(APIView):
	#permission_classes = [IsSuperAdmin]

		def get(self, request):
				return Response(build_student_openapi_schema(), status=status.HTTP_200_OK)


class StudentSwaggerUIView(APIView):
		#permission_classes = [IsSuperAdmin]

		def get(self, request):
				spec_url = request.build_absolute_uri("/api/v1/students/swagger/")
				html = """
<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1" />
		<title>SGEP Students API — Swagger UI</title>
		<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4.18.3/swagger-ui.css" />
	</head>
	<body>
		<div id="swagger-ui"></div>
		<script src="https://unpkg.com/swagger-ui-dist@4.18.3/swagger-ui-bundle.js"></script>
		<script>
			const ui = SwaggerUIBundle({
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
