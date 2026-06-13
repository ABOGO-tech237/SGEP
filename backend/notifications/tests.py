from __future__ import annotations

from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from notifications.tasks import (
	notify_account_reactivated_task,
	notify_account_suspended_task,
	notify_bulletin_published_task,
	notify_parent_absence_task,
	notify_payment_overdue_task,
	send_parent_credentials_task,
)


@override_settings(DEFAULT_FROM_EMAIL="noreply@sgep.test")
class NotificationTaskTests(SimpleTestCase):
	def test_notify_parent_absence_task_dry_run(self):
		parent = {"id": "parent-1", "email": "parent@example.com"}

		with patch("notifications.tasks.UserRepository.list_by_student_id", return_value=[parent]), patch(
			"notifications.tasks.NotificationRepository.create",
			return_value={"id": "notif-1"},
		) as create_mock, patch("notifications.tasks.NotificationRepository.update") as update_mock, patch(
			"notifications.tasks.send_mail"
		) as mail_mock:
			notify_parent_absence_task("stu-1", "2026-06-01", "absence", dry_run=True)

		create_mock.assert_called_once()
		update_mock.assert_called_once()
		mail_mock.assert_not_called()

	def test_send_parent_credentials_task_dry_run(self):
		with patch(
			"notifications.tasks.NotificationRepository.create",
			return_value={"id": "notif-2"},
		) as create_mock, patch("notifications.tasks.NotificationRepository.update") as update_mock, patch(
			"notifications.tasks.send_mail"
		) as mail_mock:
			send_parent_credentials_task("parent-1", "parent@example.com", "TempPass123!", dry_run=True)

		create_mock.assert_called_once()
		update_mock.assert_called_once()
		mail_mock.assert_not_called()

	def test_notify_bulletin_published_task_dry_run(self):
		parent = {"id": "parent-1", "email": "parent@example.com"}

		with patch("notifications.tasks.UserRepository.list_by_student_id", return_value=[parent]), patch(
			"notifications.tasks.NotificationRepository.create",
			return_value={"id": "notif-3"},
		), patch("notifications.tasks.NotificationRepository.update"), patch("notifications.tasks.send_mail") as mail_mock:
			notify_bulletin_published_task("stu-1", "Trimestre 1", dry_run=True)

		mail_mock.assert_not_called()

	def test_notify_payment_overdue_task_dry_run(self):
		with patch(
			"notifications.tasks.NotificationRepository.create",
			return_value={"id": "notif-4"},
		), patch("notifications.tasks.NotificationRepository.update"), patch("notifications.tasks.send_mail") as mail_mock:
			notify_payment_overdue_task("inv-1", 15, dry_run=True)

		mail_mock.assert_not_called()

	def test_notify_account_suspended_task_dry_run(self):
		parent = {"id": "parent-1", "email": "parent@example.com"}

		with patch("notifications.tasks.UserRepository.get_by_id", return_value=parent), patch(
			"notifications.tasks.NotificationRepository.create",
			return_value={"id": "notif-5"},
		), patch("notifications.tasks.NotificationRepository.update"), patch("notifications.tasks.send_mail") as mail_mock:
			notify_account_suspended_task("parent-1", dry_run=True)

		mail_mock.assert_not_called()

	def test_notify_account_reactivated_task_dry_run(self):
		parent = {"id": "parent-1", "email": "parent@example.com"}

		with patch("notifications.tasks.UserRepository.get_by_id", return_value=parent), patch(
			"notifications.tasks.NotificationRepository.create",
			return_value={"id": "notif-6"},
		), patch("notifications.tasks.NotificationRepository.update"), patch("notifications.tasks.send_mail") as mail_mock:
			notify_account_reactivated_task("parent-1", dry_run=True)

		mail_mock.assert_not_called()

	def test_tasks_have_max_retries(self):
		self.assertEqual(notify_parent_absence_task.max_retries, 3)
		self.assertEqual(send_parent_credentials_task.max_retries, 3)
