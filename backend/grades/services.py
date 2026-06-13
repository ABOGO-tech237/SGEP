from __future__ import annotations

from datetime import datetime, timezone

from core.exceptions import NotFoundError
from students.repository import StudentRepository

from .repository import GradeRepository, SubjectRepository


class GradeService:
	@staticmethod
	def _now() -> str:
		return datetime.now(timezone.utc).isoformat()

	@staticmethod
	def _student_ids_for_class(class_id: str) -> list[str]:
		response = StudentRepository.list(class_id=class_id, is_active=True, page_size=500)
		return [student["id"] for student in response.get("documents", [])]

	@staticmethod
	def list(
		class_id: str | None = None,
		subject_id: str | None = None,
		period_id: str | None = None,
		student_id: str | None = None,
	) -> list[dict]:
		student_ids = None
		if class_id:
			student_ids = GradeService._student_ids_for_class(class_id)
			if not student_ids:
				return []

		grades = GradeRepository.list(
			subject_id=subject_id,
			period_id=period_id,
			student_id=student_id,
			student_ids=student_ids,
		)
		return [GradeService._with_period_id(grade) for grade in grades]

	@staticmethod
	def _with_period_id(grade: dict) -> dict:
		result = dict(grade)
		result["period_id"] = grade.get("sequence", "")
		return result

	@staticmethod
	def get(grade_id: str) -> dict:
		grade = GradeRepository.get(grade_id)
		if not grade:
			raise NotFoundError(f"Note {grade_id} introuvable.")
		return GradeService._with_period_id(grade)

	@staticmethod
	def create(validated_data: dict, recorded_by: str) -> dict:
		subject = SubjectRepository.get(validated_data["subject_id"])
		coefficient = float(subject.get("coefficient", 1)) if subject else float(validated_data.get("coefficient", 1))

		payload = {
			"student_id": validated_data["student_id"],
			"subject_id": validated_data["subject_id"],
			"sequence": validated_data["period_id"],
			"value": float(validated_data["value"]),
			"coefficient": coefficient,
			"academic_year_id": validated_data.get("academic_year_id", ""),
			"recorded_by": recorded_by,
			"comments": validated_data.get("comments", ""),
			"is_deleted": False,
			"created_at": GradeService._now(),
			"updated_at": GradeService._now(),
		}
		return GradeService._with_period_id(GradeRepository.create(payload))

	@staticmethod
	def update(grade_id: str, validated_data: dict) -> dict:
		GradeService.get(grade_id)
		payload: dict = {"updated_at": GradeService._now()}

		if "value" in validated_data:
			payload["value"] = float(validated_data["value"])
		if "comments" in validated_data:
			payload["comments"] = validated_data["comments"]
		if "period_id" in validated_data:
			payload["sequence"] = validated_data["period_id"]

		return GradeService._with_period_id(GradeRepository.update(grade_id, payload))

	@staticmethod
	def bulk_input(validated_data: list[dict], recorded_by: str) -> list[dict]:
		payloads: list[dict] = []
		for item in validated_data:
			subject = SubjectRepository.get(item["subject_id"])
			coefficient = float(subject.get("coefficient", 1)) if subject else 1.0
			payloads.append(
				{
					"student_id": item["student_id"],
					"subject_id": item["subject_id"],
					"sequence": item["period_id"],
					"value": float(item["value"]),
					"coefficient": coefficient,
					"academic_year_id": item.get("academic_year_id", ""),
					"recorded_by": recorded_by,
					"comments": item.get("comments", ""),
					"is_deleted": False,
					"created_at": GradeService._now(),
					"updated_at": GradeService._now(),
				}
			)
		created = GradeRepository.bulk_create(payloads)
		from core.audit import log_action

		log_action(recorded_by, "CREATE", "grades", "bulk", {"count": len(created)}, "")
		return [GradeService._with_period_id(grade) for grade in created]

	@staticmethod
	def calculate_averages(class_id: str, period_id: str) -> dict[str, dict]:
		student_ids = GradeService._student_ids_for_class(class_id)
		if not student_ids:
			return {}

		grades = GradeRepository.list(student_ids=student_ids, period_id=period_id)
		student_grades: dict[str, list[dict]] = {sid: [] for sid in student_ids}

		for grade in grades:
			student_grades.setdefault(grade["student_id"], []).append(grade)

		results: dict[str, dict] = {}
		for student_id, student_grade_list in student_grades.items():
			if not student_grade_list:
				results[student_id] = {"average": 0.0, "rank": 0, "subject_averages": {}}
				continue

			subject_totals: dict[str, dict] = {}
			weighted_sum = 0.0
			total_coef = 0.0

			for grade in student_grade_list:
				subject_id = grade["subject_id"]
				value = float(grade.get("value", 0))
				coef = float(grade.get("coefficient", 1))

				if subject_id not in subject_totals:
					subject_totals[subject_id] = {"weighted_sum": 0.0, "total_coef": 0.0}
				subject_totals[subject_id]["weighted_sum"] += value * coef
				subject_totals[subject_id]["total_coef"] += coef
				weighted_sum += value * coef
				total_coef += coef

			subject_averages = {
				subject_id: round(data["weighted_sum"] / data["total_coef"], 2)
				if data["total_coef"]
				else 0.0
				for subject_id, data in subject_totals.items()
			}
			average = round(weighted_sum / total_coef, 2) if total_coef else 0.0
			results[student_id] = {
				"average": average,
				"rank": 0,
				"subject_averages": subject_averages,
			}

		sorted_students = sorted(results.items(), key=lambda item: item[1]["average"], reverse=True)
		current_rank = 0
		previous_average: float | None = None
		for index, (student_id, data) in enumerate(sorted_students, start=1):
			if data["average"] != previous_average:
				current_rank = index
				previous_average = data["average"]
			results[student_id]["rank"] = current_rank

		return results

	@staticmethod
	def grades_for_student(student_id: str, period_id: str | None = None) -> list[dict]:
		grades = GradeRepository.list(student_id=student_id, period_id=period_id)
		return [GradeService._with_period_id(grade) for grade in grades]


class ReportCardService:
	@staticmethod
	def _now() -> str:
		return datetime.now(timezone.utc).isoformat()

	@staticmethod
	def create_generation_job(class_id: str, period_id: str, requested_by: str, academic_year_id: str = "") -> dict:
		import json
		from students.repository import ReportJobRepository

		return ReportJobRepository.create(
			{
				"type": "report_cards",
				"status": "pending",
				"requested_by": requested_by,
				"file_path": "",
				"error": "",
				"params": json.dumps(
					{"class_id": class_id, "period_id": period_id, "academic_year_id": academic_year_id},
					ensure_ascii=True,
				),
				"is_deleted": False,
				"created_at": ReportCardService._now(),
				"updated_at": ReportCardService._now(),
			}
		)

	@staticmethod
	def get_job_status(job_id: str) -> dict:
		from students.repository import ReportJobRepository

		job = ReportJobRepository.get(job_id)
		if not job:
			return {"status": "not_found", "progress": 0}
		status = job.get("status", "pending")
		progress = 100 if status == "done" else 50 if status == "processing" else 0
		return {"status": status, "progress": progress, "file_path": job.get("file_path", "")}

	@staticmethod
	def list_for_student(student_id: str, period_id: str | None = None) -> list[dict]:
		from .repository import ReportCardRepository

		cards = ReportCardRepository.list(student_id=student_id, period_id=period_id)
		for card in cards:
			card["period_id"] = card.get("sequence", "")
		return cards

	@staticmethod
	def get(report_card_id: str) -> dict:
		from .repository import ReportCardRepository

		card = ReportCardRepository.get(report_card_id)
		if not card:
			raise NotFoundError(f"Bulletin {report_card_id} introuvable.")
		card["period_id"] = card.get("sequence", "")
		return card

	@staticmethod
	def publish(report_card_id: str) -> dict:
		from .repository import ReportCardRepository
		from notifications.tasks import notify_bulletin_published_task

		card = ReportCardService.get(report_card_id)
		updated = ReportCardRepository.update(
			report_card_id,
			{"status": "published", "updated_at": ReportCardService._now()},
		)
		updated["period_id"] = updated.get("sequence", "")
		notify_bulletin_published_task.delay(card["student_id"], card.get("sequence", ""))
		return updated
