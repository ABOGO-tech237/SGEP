from django.urls import path

from grades import views

urlpatterns = [
    path("", views.GradesListCreateView.as_view(), name="grades-list-create"),
    path("bulk/", views.GradesBulkCreateView.as_view(), name="grades-bulk-create"),
    path("averages/", views.GradeAveragesView.as_view(), name="grades-averages"),
    path("<str:grade_id>/", views.GradeDetailView.as_view(), name="grade-detail"),
    path("report-cards/generate/", views.ReportCardGenerateView.as_view(), name="reportcards-generate"),
    path("report-cards/<str:job_id>/status/", views.ReportCardStatusView.as_view(), name="reportcards-status"),
    path("report-cards/<str:card_id>/download/", views.ReportCardDownloadView.as_view(), name="reportcards-download"),
    path("report-cards/<str:card_id>/publish/", views.ReportCardPublishView.as_view(), name="reportcards-publish"),
]
