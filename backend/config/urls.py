from django.contrib import admin
from django.urls import include, path

api_v1_urlpatterns = [
    path("", include("accounts.urls")),
    path("", include("students.urls")),
    path("", include("attendance.urls")),
    path("grades/", include("grades.urls")),
    path("", include("reports.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((api_v1_urlpatterns, "api"), namespace="v1")),
]