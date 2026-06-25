from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsSuperAdmin

from .serializers import ClassSerializer, SubjectSerializer
from .services import ClassService, SubjectService


class ClassListCreateView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		classes = ClassService.list(
			academic_year_id=request.query_params.get("academic_year_id"),
			level_id=request.query_params.get("level_id"),
		)
		return Response(ClassSerializer(classes, many=True).data)

	def post(self, request):
		serializer = ClassSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		item = ClassService.create(serializer.validated_data)
		return Response(ClassSerializer(item).data, status=status.HTTP_201_CREATED)


class ClassDetailView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request, pk: str):
		return Response(ClassSerializer(ClassService.get(pk)).data)

	def patch(self, request, pk: str):
		serializer = ClassSerializer(data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		item = ClassService.update(pk, serializer.validated_data)
		return Response(ClassSerializer(item).data)


class SubjectListCreateView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request):
		subjects = SubjectService.list(class_id=request.query_params.get("class_id"))
		return Response(SubjectSerializer(subjects, many=True).data)

	def post(self, request):
		serializer = SubjectSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		item = SubjectService.create(serializer.validated_data)
		return Response(SubjectSerializer(item).data, status=status.HTTP_201_CREATED)


class SubjectDetailView(APIView):
	permission_classes = [IsSuperAdmin]

	def get(self, request, pk: str):
		return Response(SubjectSerializer(SubjectService.get(pk)).data)

	def patch(self, request, pk: str):
		serializer = SubjectSerializer(data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		item = SubjectService.update(pk, serializer.validated_data)
		return Response(SubjectSerializer(item).data)
