from django.urls import path

from .views import ClassDetailView, ClassListCreateView, SubjectDetailView, SubjectListCreateView

urlpatterns = [
	path("classes/", ClassListCreateView.as_view(), name="classes-list"),
	path("classes/<str:pk>/", ClassDetailView.as_view(), name="classes-detail"),
	path("subjects/", SubjectListCreateView.as_view(), name="subjects-list"),
	path("subjects/<str:pk>/", SubjectDetailView.as_view(), name="subjects-detail"),
]
