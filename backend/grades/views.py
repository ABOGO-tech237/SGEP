from __future__ import annotations

import os

from django.http import FileResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import ROLE_PARENT, ROLE_SUPERADMIN
from accounts.permissions import IsActiveParent, IsSuperAdmin
from core.exceptions import AccountSuspendedError, NotFoundError

from .serializers import (
	BulkGradeCreateSerializer,
	GradeCreateSerializer,
	GradeSerializer,
	ReportCardGenerateSerializer,
	ReportCardSerializer,
)
from .services import GradeService, ReportCardService
from .tasks import generate_class_report_cards_task


class GradeListCreateView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		grades = GradeService.list(
			class_id=request.query_params.get("class_id"),
			subject_id=request.query_params.get("subject_id"),
			period_id=request.query_params.get("period_id"),
		)
		return Response(GradeSerializer(grades, many=True).data)

	def post(self, request):
		serializer = GradeCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		grade = GradeService.create(serializer.validated_data, str(request.user.id))
		return Response(GradeSerializer(grade).data, status=status.HTTP_201_CREATED)


class GradeDetailView(APIView):
	permission_classes = [IsSuperAdmin]

	def put(self, request, pk: str):
		serializer = GradeCreateSerializer(data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		grade = GradeService.update(pk, serializer.validated_data)
		return Response(GradeSerializer(grade).data)


class GradeBulkCreateView(APIView):
	permission_classes = [IsSuperAdmin]

	def post(self, request):
		serializer = BulkGradeCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		grades = GradeService.bulk_input(serializer.validated_data["grades"], str(request.user.id))
		return Response(GradeSerializer(grades, many=True).data, status=status.HTTP_201_CREATED)


class ReportCardGenerateView(APIView):
	permission_classes = [IsSuperAdmin]

	def post(self, request):
		serializer = ReportCardGenerateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		job = ReportCardService.create_generation_job(
			data["class_id"],
			data["period_id"],
			str(request.user.id),
			data.get("academic_year_id", ""),
		)
		generate_class_report_cards_task.delay(
			data["class_id"],
			data["period_id"],
			job["id"],
			data.get("academic_year_id", ""),
		)
		return Response({"job_id": job["id"]}, status=status.HTTP_202_ACCEPTED)


class ReportCardStatusView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request, pk: str):
		return Response(ReportCardService.get_job_status(pk))


class ReportCardDownloadView(APIView):
	def get_permissions(self):
		if self.request.user.is_authenticated and self.request.user.role == ROLE_PARENT:
			return [IsActiveParent()]
		return [IsSuperAdmin()]

	def get(self, request, pk: str):
		if request.user.role == ROLE_PARENT:
			if request.user.account_status != "active":
				raise AccountSuspendedError(
					"Compte suspendu. Veuillez contacter l'administration pour renouveler l'inscription."
				)

		card = ReportCardService.get(pk)
		if request.user.role == ROLE_PARENT and card["student_id"] != request.user.student_id:
			raise NotFoundError("Bulletin introuvable.")

		file_path = card.get("file_path", "")
		if not file_path or not os.path.isfile(file_path):
			raise NotFoundError("Fichier bulletin introuvable.")

		return FileResponse(open(file_path, "rb"), as_attachment=True, filename=os.path.basename(file_path))


class ReportCardPublishView(APIView):
	permission_classes = [IsSuperAdmin]

	def post(self, request, pk: str):
		card = ReportCardService.publish(pk)
		return Response(ReportCardSerializer(card).data)
