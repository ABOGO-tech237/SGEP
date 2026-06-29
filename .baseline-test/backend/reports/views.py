from __future__ import annotations

import os

from django.http import FileResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsComptable, IsSuperAdmin
from core.exceptions import NotFoundError

from .services import ReportJobService


class ReportJobStatusView(APIView):
	def get_permissions(self):
		user = self.request.user
		if getattr(user, "role", None) in ("superadmin", "comptable"):
			return [IsComptable()]
		return [IsSuperAdmin()]

	def get(self, request, pk: str):
		return Response(ReportJobService.get_status(pk))


class ReportJobDownloadView(APIView):
	def get_permissions(self):
		user = self.request.user
		if getattr(user, "role", None) in ("superadmin", "comptable"):
			return [IsComptable()]
		return [IsSuperAdmin()]

	def get(self, request, pk: str):
		file_path = ReportJobService.get_download_path(pk)
		if not os.path.isfile(file_path):
			raise NotFoundError("Fichier export introuvable sur le disque.")
		return FileResponse(open(file_path, "rb"), as_attachment=True, filename=os.path.basename(file_path))
