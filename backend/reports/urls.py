from django.urls import path
from grades import views as grades_views

urlpatterns = [
    path("report-cards/generate/", grades_views.ReportCardGenerateView.as_view(), name="reportcards-generate"),
    path("report-cards/<str:job_id>/status/", grades_views.ReportCardStatusView.as_view(), name="reportcards-status"),
    path("report-cards/<str:card_id>/download/", grades_views.ReportCardDownloadView.as_view(), name="reportcards-download"),
    path("report-cards/<str:card_id>/publish/", grades_views.ReportCardPublishView.as_view(), name="reportcards-publish"),
]
