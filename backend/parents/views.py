from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import ACCOUNT_STATUS_SUSPENDED, ROLE_PARENT
from accounts.permissions import IsActiveParent, IsParentAny
from accounts.repository import UserRepository
from attendance.services import AttendanceService
from core.exceptions import AccountSuspendedError, NotFoundError
from finance.services import InvoiceService, PaymentService
from grades.services import GradeService, ReportCardService
from students.services import StudentService


def _check_active_parent(user) -> None:
	if user.account_status == ACCOUNT_STATUS_SUSPENDED:
		raise AccountSuspendedError(
			"Compte suspendu. Veuillez contacter l'administration pour renouveler l'inscription."
		)


def _get_linked_student_id(user) -> str:
	student_id = user.student_id
	if not student_id:
		raise NotFoundError("Aucun élève lié à ce compte.")
	return student_id


class ParentMeView(APIView):
	permission_classes = [IsParentAny]

	def get(self, request):
		user_payload = UserRepository.get_by_id(str(request.user.id))
		if not user_payload:
			raise NotFoundError("Compte introuvable.")
		return Response(
			{
				"id": user_payload["id"],
				"email": user_payload.get("email", ""),
				"account_status": user_payload.get("account_status", ""),
				"student_id": user_payload.get("student_id"),
			}
		)


class ParentStudentView(APIView):
	permission_classes = [IsActiveParent]

	def get(self, request):
		_check_active_parent(request.user)
		student_id = _get_linked_student_id(request.user)
		student = StudentService.get(student_id)
		return Response(student)


class ParentGradesView(APIView):
	permission_classes = [IsActiveParent]

	def get(self, request):
		_check_active_parent(request.user)
		student_id = _get_linked_student_id(request.user)
		grades = GradeService.grades_for_student(student_id, request.query_params.get("period_id"))
		return Response(grades)


class ParentAttendanceView(APIView):
	permission_classes = [IsActiveParent]

	def get(self, request):
		_check_active_parent(request.user)
		student_id = _get_linked_student_id(request.user)
		records = AttendanceService.list(student_id=student_id)
		return Response(records)


class ParentReportCardsView(APIView):
	permission_classes = [IsActiveParent]

	def get(self, request):
		_check_active_parent(request.user)
		student_id = _get_linked_student_id(request.user)
		cards = ReportCardService.list_for_student(student_id)
		return Response(cards)


class ParentReportCardDownloadView(APIView):
	permission_classes = [IsActiveParent]

	def get(self, request, pk: str):
		import os

		from django.http import FileResponse

		_check_active_parent(request.user)
		student_id = _get_linked_student_id(request.user)
		card = ReportCardService.get(pk)
		if card["student_id"] != student_id:
			raise NotFoundError("Bulletin introuvable.")

		file_path = card.get("file_path", "")
		if not file_path or not os.path.isfile(file_path):
			raise NotFoundError("Fichier bulletin introuvable.")
		return FileResponse(open(file_path, "rb"), as_attachment=True, filename=os.path.basename(file_path))


class ParentInvoicesView(APIView):
	permission_classes = [IsParentAny]

	def get(self, request):
		student_id = _get_linked_student_id(request.user)
		invoices = InvoiceService.list(student_id=student_id)
		return Response(invoices)


class ParentInvoiceReceiptView(APIView):
	permission_classes = [IsParentAny]

	def get(self, request, pk: str):
		payment = PaymentService.get(pk)
		invoice = InvoiceService.get(payment["invoice_id"])
		student_id = _get_linked_student_id(request.user)
		if invoice["student_id"] != student_id:
			raise NotFoundError("Reçu introuvable.")

		from finance.views import FinancePaymentReceiptView

		return FinancePaymentReceiptView().get(request, pk)


class ParentMessagesView(APIView):
	permission_classes = [IsActiveParent]

	def get(self, request):
		_check_active_parent(request.user)
		return Response([])

	def post(self, request):
		_check_active_parent(request.user)
		return Response({"detail": "Message envoyé."}, status=status.HTTP_201_CREATED)
