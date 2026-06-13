from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

import core.openapi  # noqa: F401 — enregistre les annotations OpenAPI

api_v1_urlpatterns = [
    path("", include("accounts.urls")),
    path("", include("students.urls")),
    path("", include("attendance.urls")),
    path("", include("grades.urls")),
    path("", include("finance.urls")),
    path("", include("parents.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((api_v1_urlpatterns, "api"), namespace="v1")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]