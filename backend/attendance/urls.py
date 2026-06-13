from django.urls import path

from .views import (
	AttendanceDetailView,
	AttendanceExportView,
	AttendanceJustifyView,
	AttendanceListCreateView,
	AttendanceStatsView,
)

urlpatterns = [
	path("attendance/", AttendanceListCreateView.as_view(), name="attendance-list"),
	path("attendance/stats/", AttendanceStatsView.as_view(), name="attendance-stats"),
	path("attendance/export/", AttendanceExportView.as_view(), name="attendance-export"),
	path("attendance/<str:pk>/justify/", AttendanceJustifyView.as_view(), name="attendance-justify"),
	path("attendance/<str:pk>/", AttendanceDetailView.as_view(), name="attendance-detail"),
]
