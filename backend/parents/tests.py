from __future__ import annotations

from unittest.mock import ANY, patch

from django.test import TestCase

from parents.services import ParentAccountService


class ParentAccountServiceTests(TestCase):
	def setUp(self) -> None:
		self.student = {
			"id": "student-1",
			"school_id": "school-1",
			"class_id": "class-1",
			"academic_year_id": "ay-1",
		}

	@patch("parents.services.send_parent_credentials_task")
	@patch("parents.services.ParentStudentRepository.create")
	@patch("parents.services.ParentRepository.create")
	@patch("parents.services.ParentRepository.get_by_email", return_value=None)
	@patch("parents.services.UserRepository.create")
	def test_create_from_student_creates_user_parent_and_link(
		self,
		mock_user_create,
		mock_parent_get_by_email,
		mock_parent_create,
		mock_parent_student_create,
		mock_credentials_task,
	) -> None:
		mock_user_create.return_value = {"id": "user-1", "email": "parent@example.com"}
		mock_parent_create.return_value = {"id": "parent-1", "user_id": "user-1"}
		mock_parent_student_create.return_value = {"id": "link-1", "user_id": "user-1"}

		with patch("parents.services.ParentStudentRepository.find_link", return_value=None):
			result = ParentAccountService.create_from_student(
				self.student,
				[
					{
						"first_name": "Marie",
						"last_name": "Dupont",
						"relationship": "Mere",
						"phone": "+237600000000",
						"phone2": "+237600000001",
						"email": "parent@example.com",
					}
				],
			)

		self.assertEqual(result[0]["user_id"], "user-1")
		mock_parent_get_by_email.assert_called_once_with("parent@example.com")
		mock_parent_create.assert_called_once()
		mock_parent_student_create.assert_called_once()
		mock_credentials_task.delay.assert_called_once()

	@patch("parents.services.ParentStudentRepository.list_by_student_id")
	@patch("parents.services.UserRepository.update")
	@patch("parents.services.send_account_suspended_notification_task")
	def test_suspend_sets_linked_parents_to_suspended(
		self,
		mock_suspended_task,
		mock_user_update,
		mock_links,
	) -> None:
		mock_links.return_value = [
			{"id": "link-1", "user_id": "user-1"},
			{"id": "link-2", "user_id": "user-2"},
		]
		mock_user_update.side_effect = [
			{"id": "user-1", "account_status": "suspended"},
			{"id": "user-2", "account_status": "suspended"},
		]

		updated = ParentAccountService.suspend("student-1")

		self.assertEqual(len(updated), 2)
		self.assertEqual(updated[0]["account_status"], "suspended")
		mock_user_update.assert_any_call("user-1", {"account_status": "suspended", "updated_at": ANY})
		mock_user_update.assert_any_call("user-2", {"account_status": "suspended", "updated_at": ANY})
		mock_suspended_task.delay.assert_called_once_with("student-1")

	@patch("parents.services.ParentStudentRepository.list_by_student_id")
	@patch("parents.services.UserRepository.update")
	@patch("parents.services.send_account_reactivated_notification_task")
	def test_reactivate_sets_linked_parents_to_active(
		self,
		mock_reactivated_task,
		mock_user_update,
		mock_links,
	) -> None:
		mock_links.return_value = [{"id": "link-1", "user_id": "user-1"}]
		mock_user_update.return_value = {"id": "user-1", "account_status": "active"}

		updated = ParentAccountService.reactivate("student-1")

		self.assertEqual(len(updated), 1)
		self.assertEqual(updated[0]["account_status"], "active")
		mock_reactivated_task.delay.assert_called_once_with("student-1")

	@patch("parents.services.ParentStudentRepository.find_link", return_value={"id": "link-1", "user_id": "user-1"})
	@patch("parents.services.ParentStudentRepository.create")
	@patch("parents.services.UserRepository.create")
	@patch("parents.services.ParentRepository.get_by_email")
	def test_create_from_student_skips_duplicate_link(
		self,
		mock_parent_get_by_email,
		mock_user_create,
		mock_link_create,
		mock_find_link,
	) -> None:
		result = ParentAccountService.create_from_student(
			self.student,
			[
				{
					"first_name": "Marie",
					"last_name": "Dupont",
					"relationship": "Mere",
					"phone": "+237600000000",
					"email": "parent@example.com",
				}
			],
		)

		self.assertEqual(result[0]["id"], "link-1")
		mock_parent_get_by_email.assert_not_called()
		mock_user_create.assert_not_called()
		mock_link_create.assert_not_called()
