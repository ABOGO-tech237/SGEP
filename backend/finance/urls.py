from django.urls import path

from .views import (
	FinanceDashboardView,
	FinanceExportExcelView,
	FinanceInvoiceGenerateView,
	FinanceInvoiceListView,
	FinanceOverdueView,
	FinancePaymentCreateView,
	FinancePaymentReceiptView,
)

urlpatterns = [
	path("finance/invoices/", FinanceInvoiceListView.as_view(), name="finance-invoices"),
	path("finance/invoices/generate/", FinanceInvoiceGenerateView.as_view(), name="finance-invoices-generate"),
	path("finance/payments/", FinancePaymentCreateView.as_view(), name="finance-payments"),
	path("finance/payments/<str:pk>/receipt/", FinancePaymentReceiptView.as_view(), name="finance-payment-receipt"),
	path("finance/overdue/", FinanceOverdueView.as_view(), name="finance-overdue"),
	path("finance/dashboard/", FinanceDashboardView.as_view(), name="finance-dashboard"),
	path("finance/export/excel/", FinanceExportExcelView.as_view(), name="finance-export-excel"),
]
