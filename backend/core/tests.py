from __future__ import annotations

from unittest.mock import patch

from django.test import SimpleTestCase

from core.audit import log_action


class AuditTests(SimpleTestCase):
	def test_log_action_creates_document(self):
		with patch("core.audit.databases.create_document") as create_mock:
			log_action("user-1", "CREATE", "students", "stu-1", {"matricule": "MAT-001"}, "127.0.0.1")

		create_mock.assert_called_once()
		payload = create_mock.call_args[0][3]
		self.assertEqual(payload["user_id"], "user-1")
		self.assertEqual(payload["action"], "CREATE")
		self.assertEqual(payload["resource_type"], "students")
