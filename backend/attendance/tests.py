from __future__ import annotations

import uuid
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from accounts.models import ACCOUNT_STATUS_ACTIVE, ROLE_SUPERADMIN, User
from attendance.serializers import AttendanceCreateSerializer, JustifySerializer
from attendance.services import AttendanceService


class AttendanceServiceTests(SimpleTestCase):
	def test_record_absence_creates_record_and_notifies_parent(self):
		with patch(
			"attendance.services.AttendanceRepository.create",
			return_value={
				"id": "att-1",
				"student_id": "stu-1",
				"class_id": "class-a",
				"date": "2026-06-01T00:00:00+00:00",
				"status": "ABSENT",
				"reason": "Maladie",
				"academic_year_id": "ay-2026",
				"recorded_by": "admin-1",
			},
		) as create_mock, patch("attendance.services.notify_parent_absence_task.delay") as delay_mock:
			record = AttendanceService.record_absence(
				student_id="stu-1",
				class_id="class-a",
				date_value="2026-06-01T00:00:00+00:00",
				absence_type="absence",
				motif="Maladie",
				recorded_by="admin-1",
				academic_year_id="ay-2026",
			)

		self.assertEqual(record["id"], "att-1")
		create_mock.assert_called_once()
		delay_mock.assert_called_once_with("stu-1", "2026-06-01T00:00:00+00:00", "absence")

	def test_justify_updates_status(self):
		with patch("attendance.services.AttendanceRepository.get", return_value={"id": "att-1"}), patch(
			"attendance.services.AttendanceRepository.update",
			return_value={"id": "att-1", "status": "ABSENT_JUSTIFIE", "reason": "Certificat médical"},
		) as update_mock:
			record = AttendanceService.justify("att-1", "Certificat médical")

		self.assertEqual(record["status"], "ABSENT_JUSTIFIE")
		update_mock.assert_called_once()

	def test_get_stats_calculates_rate(self):
		with patch(
			"attendance.services.AttendanceRepository.get_stats",
			return_value=[
				{"student_id": "stu-1", "absences": 2, "retards": 1, "justified": 0},
			],
		):
			stats = AttendanceService.get_stats(
				"class-a",
				"2026-06-01T00:00:00+00:00",
				"2026-06-05T00:00:00+00:00",
			)

		self.assertEqual(len(stats), 1)
		self.assertEqual(stats[0]["rate"], 40.0)


class AttendanceSerializerTests(SimpleTestCase):
	def test_create_serializer_validates_type(self):
		payload = {
			"student_id": "stu-1",
			"class_id": "class-a",
			"date": "2026-06-01T00:00:00+00:00",
			"type": "absence",
			"motif": "Maladie",
			"academic_year_id": "ay-2026",
		}
		serializer = AttendanceCreateSerializer(data=payload)
		self.assertTrue(serializer.is_valid())

	def test_create_serializer_rejects_invalid_type(self):
		payload = {
			"student_id": "stu-1",
			"class_id": "class-a",
			"date": "2026-06-01T00:00:00+00:00",
			"type": "invalid",
			"academic_year_id": "ay-2026",
		}
		serializer = AttendanceCreateSerializer(data=payload)
		self.assertFalse(serializer.is_valid())
		self.assertIn("type", serializer.errors)

	def test_justify_serializer_requires_motif(self):
		serializer = JustifySerializer(data={"motif": "Certificat"})
		self.assertTrue(serializer.is_valid())


class AttendanceApiTests(SimpleTestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User(
			id=uuid.uuid4(),
			email="admin@example.com",
			role=ROLE_SUPERADMIN,
			account_status=ACCOUNT_STATUS_ACTIVE,
		)
		self.client.force_authenticate(user=self.user)

	def test_get_attendance_list(self):
		with patch(
			"attendance.views.AttendanceService.list",
			return_value=[
				{
					"id": "att-1",
					"student_id": "stu-1",
					"class_id": "class-a",
					"date": "2026-06-01T00:00:00+00:00",
					"status": "ABSENT",
					"reason": "",
					"academic_year_id": "ay-2026",
					"recorded_by": "admin-1",
				}
			],
		):
			response = self.client.get("/api/v1/attendance/?class_id=class-a")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["type"], "absence")

	def test_post_attendance_create(self):
		payload = {
			"student_id": "stu-1",
			"class_id": "class-a",
			"date": "2026-06-01T00:00:00+00:00",
			"type": "retard",
			"motif": "Transport",
			"academic_year_id": "ay-2026",
		}

		with patch(
			"attendance.views.AttendanceService.record_absence",
			return_value={
				"id": "att-2",
				"student_id": "stu-1",
				"class_id": "class-a",
				"date": "2026-06-01T00:00:00+00:00",
				"status": "RETARD",
				"reason": "Transport",
				"academic_year_id": "ay-2026",
				"recorded_by": str(self.user.id),
			},
		) as record_mock:
			response = self.client.post("/api/v1/attendance/", payload, format="json")

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["type"], "retard")
		record_mock.assert_called_once()

	def test_put_attendance_update(self):
		with patch(
			"attendance.views.AttendanceService.update",
			return_value={
				"id": "att-1",
				"student_id": "stu-1",
				"class_id": "class-a",
				"date": "2026-06-01T00:00:00+00:00",
				"status": "ABSENT",
				"reason": "Mis à jour",
				"academic_year_id": "ay-2026",
				"recorded_by": "admin-1",
			},
		):
			response = self.client.put(
				"/api/v1/attendance/att-1/",
				{"motif": "Mis à jour"},
				format="json",
			)

		self.assertEqual(response.status_code, 200)

	def test_get_attendance_stats(self):
		with patch(
			"attendance.views.AttendanceService.get_stats",
			return_value=[
				{"student_id": "stu-1", "absences": 1, "retards": 0, "justified": 0, "rate": 20.0},
			],
		):
			response = self.client.get(
				"/api/v1/attendance/stats/?class_id=class-a&date_from=2026-06-01T00:00:00+00:00&date_to=2026-06-05T00:00:00+00:00"
			)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data[0]["rate"], 20.0)

	def test_export_dispatches_celery_task(self):
		with patch("attendance.views.AttendanceService.create_export_job", return_value={"id": "job-1"}) as job_mock, patch(
			"attendance.views.generate_attendance_export_task.delay"
		) as delay_mock:
			response = self.client.get("/api/v1/attendance/export/?format=pdf")

		self.assertEqual(response.status_code, 202)
		self.assertEqual(response.data["job_id"], "job-1")
		job_mock.assert_called_once()
		delay_mock.assert_called_once()
