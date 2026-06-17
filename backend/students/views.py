from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsSuperAdmin

from .serializers import (
    StudentCreateSerializer,
    StudentEnrollSerializer,
    StudentListSerializer,
    StudentPromoteSerializer,
    StudentSerializer,
)
from .services import StudentService
from .tasks import generate_students_export_task


class StudentListCreateView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        raw_is_active = request.query_params.get("is_active")
        is_active = None
        if raw_is_active is not None:
            is_active = raw_is_active.lower() == "true"

        result = StudentService.list(
            class_id=request.query_params.get("class_id"),
            academic_year_id=request.query_params.get("academic_year_id"),
            is_active=is_active,
            search=request.query_params.get("search"),
            page=request.query_params.get("page", 1),
            page_size=request.query_params.get("page_size", 20),
        )
        serializer = StudentListSerializer(result["items"], many=True)
        return Response(
            {
                "items": serializer.data,
                "total": result.get("total", 0),
                "page": result.get("page", 1),
                "page_size": result.get("page_size", 20),
            }
        )

    def post(self, request):
        serializer = StudentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = StudentService.create(serializer.validated_data)
        return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)


class StudentDetailView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, pk: str):
        student = StudentService.get(pk)
        return Response(StudentSerializer(student).data)

    def patch(self, request, pk: str):
        serializer = StudentCreateSerializer(data=request.data, partial=True, context={"student_id": pk})
        serializer.is_valid(raise_exception=True)
        student = StudentService.update(pk, serializer.validated_data)
        return Response(StudentSerializer(student).data)

    def delete(self, request, pk: str):
        StudentService.soft_delete(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentHistoryView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, pk: str):
        return Response({"student_id": pk, "history": StudentService.history(pk)})


class StudentEnrollView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, pk: str):
        serializer = StudentEnrollSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = StudentService.enroll(
            pk,
            serializer.validated_data["class_id"],
            serializer.validated_data["academic_year_id"],
        )
        return Response(StudentSerializer(student).data, status=status.HTTP_200_OK)


class StudentPromoteView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, pk: str):
        serializer = StudentPromoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = StudentService.promote(pk, serializer.validated_data["target_class_id"])
        return Response(StudentSerializer(student).data, status=status.HTTP_200_OK)


class StudentExportPDFView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        job = StudentService.create_export_job("pdf", str(request.user.id), dict(request.query_params))
        generate_students_export_task.delay(job["id"], "pdf", dict(request.query_params))
        return Response({"job_id": job["id"]}, status=status.HTTP_202_ACCEPTED)


class StudentExportExcelView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        job = StudentService.create_export_job("excel", str(request.user.id), dict(request.query_params))
        generate_students_export_task.delay(job["id"], "excel", dict(request.query_params))
        return Response({"job_id": job["id"]}, status=status.HTTP_202_ACCEPTED)

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
