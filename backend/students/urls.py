from django.urls import path

from students.views import (
    StudentDetailView,
    StudentEnrollView,
    StudentExportExcelView,
    StudentExportPdfView,
    StudentHistoryView,
    StudentListView,
    StudentPromoteView,
    StudentSwaggerView,
    StudentSwaggerUIView,
)

urlpatterns = [
    path("students/", StudentListView.as_view(), name="student-list"),
    path("students/export/pdf/", StudentExportPdfView.as_view(), name="student-export-pdf"),
    path("students/export/excel/", StudentExportExcelView.as_view(), name="student-export-excel"),
    path("students/swagger/", StudentSwaggerView.as_view(), name="student-swagger"),
    path("students/swagger/ui/", StudentSwaggerUIView.as_view(), name="student-swagger-ui"),
    path("students/<str:student_id>/", StudentDetailView.as_view(), name="student-detail"),
    path("students/<str:student_id>/history/", StudentHistoryView.as_view(), name="student-history"),
    path("students/<str:student_id>/enroll/", StudentEnrollView.as_view(), name="student-enroll"),
    path("students/<str:student_id>/promote/", StudentPromoteView.as_view(), name="student-promote"),
]