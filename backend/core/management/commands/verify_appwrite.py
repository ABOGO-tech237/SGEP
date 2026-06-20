from __future__ import annotations

import uuid
from datetime import datetime, timezone

from django.core.management.base import BaseCommand

from core.appwrite_test_utils import is_appwrite_configured
from core.appwrite_utils import total_of
from config.appwrite_client import databases
from django.conf import settings


class Command(BaseCommand):
	help = "Vérifie la connexion Appwrite Cloud et affiche l'état des collections."

	def handle(self, *args, **options):
		if not is_appwrite_configured():
			self.stdout.write(
				self.style.ERROR(
					"Appwrite non configuré. Renseignez APPWRITE_ENDPOINT, APPWRITE_PROJECT_ID "
					"et APPWRITE_API_KEY dans backend/.env (sans placeholders)."
				)
			)
			return

		self.stdout.write(self.style.SUCCESS("Connexion Appwrite Cloud"))
		self.stdout.write(f"  Endpoint  : {settings.APPWRITE_ENDPOINT}")
		self.stdout.write(f"  Project   : {settings.APPWRITE_PROJECT_ID}")
		self.stdout.write(f"  Database  : {settings.APPWRITE_DB_ID}")

		collections = [
			"schools",
			"academic_years",
			"classes",
			"students",
			"users",
			"grades",
			"attendance",
			"invoices",
			"payments",
			"report_jobs",
			"audit_logs",
		]

		for collection_id in collections:
			try:
				response = databases.list_documents(
					settings.APPWRITE_DB_ID,
					collection_id,
					[],
				)
				total = total_of(response)
				self.stdout.write(self.style.SUCCESS(f"  ✓ {collection_id:<18} {total} document(s)"))
			except Exception as exc:
				self.stdout.write(self.style.ERROR(f"  ✗ {collection_id:<18} {exc}"))

		self.stdout.write("")
		self.stdout.write("Pour lancer les tests d'intégration :")
		self.stdout.write("  python manage.py test core.tests_appwrite_integration -v 2")
