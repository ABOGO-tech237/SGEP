from __future__ import annotations

import os
import unittest
from functools import wraps

from django.conf import settings


PLACEHOLDER_MARKERS = ("<", "YOUR_", "your-", "change-me", "example.com")


def _looks_like_placeholder(value: str) -> bool:
	normalized = value.strip().lower()
	if not normalized:
		return True
	return any(marker.lower() in normalized for marker in PLACEHOLDER_MARKERS)


def is_appwrite_configured() -> bool:
	if os.environ.get("APPWRITE_INTEGRATION_TESTS", "").lower() in {"0", "false", "no"}:
		return False

	endpoint = settings.APPWRITE_ENDPOINT or ""
	project_id = settings.APPWRITE_PROJECT_ID or ""
	api_key = settings.APPWRITE_API_KEY or ""

	if _looks_like_placeholder(endpoint):
		return False
	if _looks_like_placeholder(project_id):
		return False
	if _looks_like_placeholder(api_key):
		return False

	return True


def skip_unless_appwrite(reason: str = "Appwrite Cloud non configuré (.env avec credentials réels requis)."):
	def decorator(test_item):
		if isinstance(test_item, type) and issubclass(test_item, unittest.TestCase):
			return unittest.skipUnless(is_appwrite_configured(), reason)(test_item)

		@wraps(test_item)
		def wrapper(*args, **kwargs):
			if not is_appwrite_configured():
				raise unittest.SkipTest(reason)
			return test_item(*args, **kwargs)

		return wrapper

	return decorator
