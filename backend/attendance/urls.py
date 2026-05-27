from django.urls import path

from attendance.views import (
    AttendanceDetailView,
    AttendanceExportView,
    AttendanceJustifyView,
    AttendanceListCreateView,
    AttendanceStatsView,
    AttendanceSwaggerUIView,
    AttendanceSwaggerView,
)

urlpatterns = [
    path("attendance/", AttendanceListCreateView.as_view(), name="attendance-list-create"),
    path("attendance/stats/", AttendanceStatsView.as_view(), name="attendance-stats"),
    path("attendance/export/", AttendanceExportView.as_view(), name="attendance-export"),
    path("attendance/<str:record_id>/", AttendanceDetailView.as_view(), name="attendance-detail"),
    path("attendance/<str:record_id>/justify/", AttendanceJustifyView.as_view(), name="attendance-justify"),
    path("attendance/swagger/", AttendanceSwaggerView.as_view(), name="attendance-swagger"),
    path("attendance/swagger/ui/", AttendanceSwaggerUIView.as_view(), name="attendance-swagger-ui"),
]
