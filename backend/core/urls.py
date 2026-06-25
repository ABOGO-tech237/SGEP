from django.urls import path

from .views import (
	AcademicYearDetailView,
	AcademicYearListCreateView,
	AdminDashboardView,
	SchoolDetailView,
	SchoolListCreateView,
)

urlpatterns = [
	path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
	path("schools/", SchoolListCreateView.as_view(), name="schools-list"),
	path("schools/<str:pk>/", SchoolDetailView.as_view(), name="schools-detail"),
	path("academic-years/", AcademicYearListCreateView.as_view(), name="academic-years-list"),
	path("academic-years/<str:pk>/", AcademicYearDetailView.as_view(), name="academic-years-detail"),
]
