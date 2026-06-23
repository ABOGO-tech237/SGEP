from django.urls import path

from .views import ReportJobDownloadView, ReportJobStatusView

urlpatterns = [
	path("reports/<str:pk>/status/", ReportJobStatusView.as_view(), name="reports-status"),
	path("reports/<str:pk>/download/", ReportJobDownloadView.as_view(), name="reports-download"),
]
