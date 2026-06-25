from __future__ import annotations

from parents.repository import MessageRepository


class MessageService:
	@staticmethod
	def list_for_parent(parent_id: str) -> list[dict]:
		return MessageRepository.list_for_user(parent_id)

	@staticmethod
	def send_from_parent(parent_id: str, subject: str, body: str, admin_id: str = "admin") -> dict:
		return MessageRepository.create(
			{
				"sender_id": parent_id,
				"recipient_id": admin_id,
				"subject": subject,
				"body": body,
			}
		)
