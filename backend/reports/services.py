from __future__ import annotations

from core.exceptions import NotFoundError

from .repository import ReportJobRepository


class ReportJobService:
	@staticmethod
	def get_status(job_id: str) -> dict:
		job = ReportJobRepository.get(job_id)
		if not job:
			raise NotFoundError(f"Tâche {job_id} introuvable.")
		status = job.get("status", "pending")
		progress = 100 if status == "done" else 50 if status == "processing" else 0
		return {
			"job_id": job_id,
			"status": status,
			"progress": progress,
			"file_path": job.get("file_path", ""),
			"error": job.get("error", ""),
			"type": job.get("type", ""),
		}

	@staticmethod
	def get_download_path(job_id: str) -> str:
		job = ReportJobRepository.get(job_id)
		if not job:
			raise NotFoundError(f"Tâche {job_id} introuvable.")
		if job.get("status") != "done":
			raise NotFoundError("Le fichier n'est pas encore disponible.")
		file_path = job.get("file_path", "")
		if not file_path:
			raise NotFoundError("Chemin de fichier introuvable.")
		return file_path
