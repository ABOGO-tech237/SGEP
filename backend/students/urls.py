from django.urls import path

from .views import (
    StudentDetailView,
    StudentEnrollView,
    StudentExportExcelView,
    StudentExportPDFView,
    StudentHistoryView,
    StudentListCreateView,
    StudentPromoteView,
)

urlpatterns = [
    path("students/", StudentListCreateView.as_view(), name="students-list"),
    path("students/export/pdf/", StudentExportPDFView.as_view(), name="students-export-pdf"),
    path("students/export/excel/", StudentExportExcelView.as_view(), name="students-export-excel"),
    path("students/<str:pk>/history/", StudentHistoryView.as_view(), name="students-history"),
    path("students/<str:pk>/enroll/", StudentEnrollView.as_view(), name="students-enroll"),
    path("students/<str:pk>/promote/", StudentPromoteView.as_view(), name="students-promote"),
    path("students/<str:pk>/", StudentDetailView.as_view(), name="students-detail"),
]