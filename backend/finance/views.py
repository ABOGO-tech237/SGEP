from __future__ import annotations

import json
import os

from django.http import FileResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsComptable
from students.repository import ReportJobRepository

from .serializers import InvoiceGenerateSerializer, InvoicePlannedPaymentSerializer, InvoiceSerializer, PaymentCreateSerializer, PaymentSerializer
from .services import InvoiceService, PaymentService
from .tasks import send_overdue_reminders_task


class FinanceInvoiceListView(APIView):
	def get_permissions(self):
		return [IsComptable()]

	def get(self, request):
		invoices = InvoiceService.list(
			student_id=request.query_params.get("student_id"),
			status=request.query_params.get("status"),
		)
		return Response(InvoiceSerializer(invoices, many=True).data)


class FinanceInvoiceGenerateView(APIView):
	permission_classes = [IsComptable]

	def post(self, request):
		serializer = InvoiceGenerateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		due_date = data.get("due_date") or None
		if data.get("class_id"):
			count = InvoiceService.generate_for_class(
				data["class_id"],
				data["fee_type_id"],
				data["academic_year_id"],
				due_date=due_date,
			)
		else:
			count = InvoiceService.generate_bulk(data["academic_year_id"], data["fee_type_id"], due_date=due_date)
		return Response({"created": count}, status=status.HTTP_201_CREATED)


class FinancePaymentCreateView(APIView):
	permission_classes = [IsComptable]

	def post(self, request):
		serializer = PaymentCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		payment = PaymentService.record(
			data["invoice_id"],
			data["amount"],
			data["method"],
			data.get("reference", ""),
			str(request.user.id),
			ip_address=getattr(request, "audit_ip", ""),
		)
		return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class FinancePaymentReceiptView(APIView):
	permission_classes = [IsComptable]

	def get(self, request, pk: str):
		payment = PaymentService.get(pk)
		file_path = payment.get("receipt_path", "")
		if not file_path or not os.path.isfile(file_path):
			return Response({"detail": "Reçu non disponible."}, status=status.HTTP_404_NOT_FOUND)
		return FileResponse(open(file_path, "rb"), as_attachment=True, filename=os.path.basename(file_path))


class FinanceOverdueView(APIView):
	permission_classes = [IsComptable]

	def get(self, request):
		return Response(InvoiceSerializer(InvoiceService.overdue(), many=True).data)


class FinanceDashboardView(APIView):
	permission_classes = [IsComptable]

	def get(self, request):
		return Response(InvoiceService.dashboard())


class FinanceExportExcelView(APIView):
	permission_classes = [IsComptable]

	def get(self, request):
		job = ReportJobRepository.create(
			{
				"type": "finance_excel",
				"status": "pending",
				"requested_by": str(request.user.id),
				"file_path": "",
				"error": "",
				"params": json.dumps(dict(request.query_params), ensure_ascii=True),
				"is_deleted": False,
				"created_at": InvoiceService._now(),
				"updated_at": InvoiceService._now(),
			}
		)
		from reports.tasks import generate_finance_export_task

		generate_finance_export_task.delay(job["id"], dict(request.query_params))
		return Response({"job_id": job["id"]}, status=status.HTTP_202_ACCEPTED)
