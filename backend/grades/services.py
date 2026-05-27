from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from appwrite.exception import AppwriteException
from django.conf import settings

from config.appwrite_client import databases
from grades.repository import GradeRepository

SUBJECTS_COLLECTION_ID = "subjects"


class GradeService:
    @staticmethod
    def bulk_input(validated_data: List[dict]) -> list[dict]:
        return GradeRepository.bulk_create(validated_data)

    @staticmethod
    def _get_subject_coefficient(subject_id: str) -> float:
        try:
            doc = databases.get_document(settings.APPWRITE_DB_ID, SUBJECTS_COLLECTION_ID, subject_id)
            return float(doc.get("coefficient", 1.0))
        except AppwriteException:
            return 1.0

    @staticmethod
    def calculate_averages(class_id: str, period_id: str) -> dict:
        # Fetch grades for the period. The repository may ignore class_id; services
        # expect repository to return only relevant grades or to be mocked in tests.
        response = GradeRepository.list(class_id=class_id, period_id=period_id)
        documents = response.get("documents", [])

        per_student: Dict[str, dict] = {}
        # structure to accumulate subject totals per student
        subj_acc: Dict[str, Dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {"sum": 0.0, "coeff": 0.0}))

        for g in documents:
            student_id = g.get("student_id")
            subject_id = g.get("subject_id")
            try:
                value = float(g.get("value", 0.0))
            except (TypeError, ValueError):
                value = 0.0

            coeff = g.get("coefficient")
            if coeff is None:
                coeff = GradeService._get_subject_coefficient(subject_id)
            try:
                coeff = float(coeff)
            except (TypeError, ValueError):
                coeff = 1.0

            subj_acc[student_id][subject_id]["sum"] += value * coeff
            subj_acc[student_id][subject_id]["coeff"] += coeff

        # compute averages per student and per subject
        results: Dict[str, dict] = {}
        for student_id, subjects in subj_acc.items():
            total_weighted = 0.0
            total_coeff = 0.0
            subject_averages: Dict[str, float] = {}
            for subject_id, data in subjects.items():
                coeff_sum = data["coeff"] or 0.0
                avg = (data["sum"] / coeff_sum) if coeff_sum else 0.0
                subject_averages[subject_id] = round(avg, 2)
                total_weighted += data["sum"]
                total_coeff += coeff_sum

            average = (total_weighted / total_coeff) if total_coeff else 0.0
            results[student_id] = {"average": round(average, 2), "subject_averages": subject_averages}

        # compute ranks (standard competition ranking: 1,2,2,4)
        sorted_students = sorted(results.items(), key=lambda kv: kv[1]["average"], reverse=True)
        ranks: Dict[str, int] = {}
        current_rank = 1
        prev_avg = None
        seen = 0
        for student_id, data in sorted_students:
            seen += 1
            avg = data["average"]
            if prev_avg is None:
                ranks[student_id] = current_rank
                prev_avg = avg
                continue
            if avg == prev_avg:
                ranks[student_id] = current_rank
            else:
                current_rank = seen
                ranks[student_id] = current_rank
                prev_avg = avg

        # attach ranks
        for sid in results:
            results[sid]["rank"] = ranks.get(sid, None)

        return results
