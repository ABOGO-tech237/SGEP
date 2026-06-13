from django.urls import path

from .views import (
	GradeBulkCreateView,
	GradeDetailView,
	GradeListCreateView,
	ReportCardDownloadView,
	ReportCardGenerateView,
	ReportCardPublishView,
	ReportCardStatusView,
)

urlpatterns = [
	path("grades/", GradeListCreateView.as_view(), name="grades-list"),
	path("grades/bulk/", GradeBulkCreateView.as_view(), name="grades-bulk"),
	path("grades/<str:pk>/", GradeDetailView.as_view(), name="grades-detail"),
	path("report-cards/generate/", ReportCardGenerateView.as_view(), name="report-cards-generate"),
	path("report-cards/<str:pk>/status/", ReportCardStatusView.as_view(), name="report-cards-status"),
	path("report-cards/<str:pk>/download/", ReportCardDownloadView.as_view(), name="report-cards-download"),
	path("report-cards/<str:pk>/publish/", ReportCardPublishView.as_view(), name="report-cards-publish"),
]
