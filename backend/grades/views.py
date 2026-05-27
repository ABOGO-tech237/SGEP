from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from accounts.permissions import IsSuperAdmin
from grades.serializers import GradeSerializer, GradeCreateSerializer, BulkGradeCreateSerializer
from grades.repository import GradeRepository
from grades.services import GradeService
from grades.repository import ReportCardRepository
from students.repository import ReportJobRepository
from grades.tasks import generate_class_report_cards_task
from django.conf import settings
from django.http import FileResponse, Http404
from config.appwrite_client import databases
from accounts.permissions import ROLE_PARENT, ROLE_SUPERADMIN


class GradesListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        class_id = request.query_params.get("class_id")
        subject_id = request.query_params.get("subject_id")
        period_id = request.query_params.get("period_id")

        response = GradeRepository.list(class_id=class_id, subject_id=subject_id, period_id=period_id)
        documents = response.get("documents", [])
        serializer = GradeSerializer(documents, many=True)
        return Response({"results": serializer.data})

    def post(self, request):
        serializer = GradeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        # map period_id -> sequence for storage
        payload["sequence"] = payload.pop("period_id")
        created = GradeRepository.bulk_create([payload])[0]
        out = GradeSerializer(created)
        return Response(out.data, status=status.HTTP_201_CREATED)


class GradeDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def put(self, request, grade_id: str):
        serializer = GradeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        payload["sequence"] = payload.pop("period_id")
        updated = GradeRepository.update(grade_id, payload)
        out = GradeSerializer(updated)
        return Response(out.data)


class GradesBulkCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request):
        serializer = BulkGradeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        grades = serializer.validated_data.get("grades", [])
        # map period_id -> sequence on each grade
        for g in grades:
            g["sequence"] = g.pop("period_id")

        created = GradeService.bulk_input(grades)
        out = GradeSerializer(created, many=True)
        return Response({"created": out.data}, status=status.HTTP_201_CREATED)


class GradeAveragesView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        class_id = request.query_params.get("class_id")
        period_id = request.query_params.get("period_id")
        if not class_id or not period_id:
            return Response({"detail": "class_id and period_id are required"}, status=status.HTTP_400_BAD_REQUEST)
        result = GradeService.calculate_averages(class_id=class_id, period_id=period_id)
        return Response(result)


class ReportCardGenerateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request):
        class_id = request.data.get("class_id")
        period_id = request.data.get("period_id")
        if not class_id or not period_id:
            return Response({"detail": "class_id and period_id are required"}, status=400)

        job = ReportJobRepository.create({
            "type": "report_cards",
            "status": "pending",
            "requested_by": str(request.user.id),
            "params": {"class_id": class_id, "period_id": period_id},
        })
        job_id = job.get("id")
        generate_class_report_cards_task.delay(class_id, period_id, job_id)
        return Response({"job_id": job_id}, status=202)


class ReportCardStatusView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request, job_id: str):
        job = ReportJobRepository.get(job_id)
        if not job:
            return Response({"detail": "not found"}, status=404)
        return Response({"status": job.get("status"), "progress": job.get("progress", 0)})


class ReportCardDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, card_id: str):
        card = ReportCardRepository.get(card_id)
        if not card:
            raise Http404()

        # permission check: superadmin or active parent owner
        user = request.user
        allowed = False
        if getattr(user, "role", None) == ROLE_SUPERADMIN:
            allowed = True
        elif getattr(user, "role", None) == ROLE_PARENT and getattr(user, "account_status", "") == "active":
            parent_user_id = card.get("parent_user_id")
            if parent_user_id and str(parent_user_id) == str(getattr(user, "id", "")):
                allowed = True

        if not allowed:
            return Response({"detail": "forbidden"}, status=403)

        file_path = card.get("file_path")
        try:
            return FileResponse(open(file_path, "rb"), as_attachment=True, filename=f"report_card_{card_id}.pdf")
        except Exception:
            raise Http404()


class ReportCardPublishView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request, card_id: str):
        card = ReportCardRepository.get(card_id)
        if not card:
            return Response({"detail": "not found"}, status=404)

        ReportCardRepository.update(card_id, {"published": True})

        # create a notification for parent if present
        parent_id = card.get("parent_user_id")
        try:
            if parent_id:
                databases.create_document(settings.APPWRITE_DB_ID, "notifications", "unique()", {
                    "user_id": parent_id,
                    "title": "Bulletin publié",
                    "message": f"Le bulletin de votre enfant est disponible.",
                    "type": "report_card",
                })
        except Exception:
            # don't fail the request if notification creation fails
            pass

        return Response({"published": True})
from django.shortcuts import render

# Create your views here.
