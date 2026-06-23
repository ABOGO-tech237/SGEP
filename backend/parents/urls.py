from django.urls import path

from .views import (
	ParentAttendanceView,
	ParentGradesView,
	ParentInvoiceReceiptView,
	ParentInvoicePlannedPaymentView,
	ParentInvoicesView,
	ParentMeView,
	ParentMessagesView,
	ParentReportCardDownloadView,
	ParentReportCardsView,
	ParentStudentView,
)

urlpatterns = [
	path("parent/me/", ParentMeView.as_view(), name="parent-me"),
	path("parent/me/student/", ParentStudentView.as_view(), name="parent-student"),
	path("parent/me/grades/", ParentGradesView.as_view(), name="parent-grades"),
	path("parent/me/attendance/", ParentAttendanceView.as_view(), name="parent-attendance"),
	path("parent/me/report-cards/", ParentReportCardsView.as_view(), name="parent-report-cards"),
	path("parent/me/report-cards/<str:pk>/download/", ParentReportCardDownloadView.as_view(), name="parent-report-card-download"),
	path("parent/me/invoices/", ParentInvoicesView.as_view(), name="parent-invoices"),
	path(
		"parent/me/invoices/<str:pk>/planned-payment-date/",
		ParentInvoicePlannedPaymentView.as_view(),
		name="parent-invoice-planned-payment",
	),
	path("parent/me/invoices/<str:pk>/receipt/", ParentInvoiceReceiptView.as_view(), name="parent-invoice-receipt"),
	path("parent/me/messages/", ParentMessagesView.as_view(), name="parent-messages"),
]
