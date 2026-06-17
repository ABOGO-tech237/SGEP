"""Appwrite service wrapper for database operations."""

from __future__ import annotations

from django.conf import settings


class AppwriteService:
    """Wrapper service for Appwrite database operations."""

    def __init__(self) -> None:
        """Initialize Appwrite client."""
        try:
            from appwrite.client import Client
            from appwrite.services.databases import Databases

            self.client = Client()
            self.client.set_endpoint(settings.APPWRITE_ENDPOINT)
            self.client.set_project(settings.APPWRITE_PROJECT_ID)
            self.client.set_key(settings.APPWRITE_API_KEY)
            self.databases = Databases(self.client)
        except Exception as exc:
            raise ImportError(f"Appwrite SDK not installed or misconfigured: {exc}") from exc

    def create_database(self, db_id: str, name: str):
        """Create a new database."""
        return self.databases.create(
            database_id=db_id,
            name=name,
        )

    def create_attribute(self, db_id: str, collection_id: str, key: str, type: str, **kwargs):
        """Create an attribute in a collection."""
        type_methods = {
            "string": self.databases.create_string_attribute,
            "email": self.databases.create_email_attribute,
            "boolean": self.databases.create_boolean_attribute,
            "integer": self.databases.create_integer_attribute,
            "float": self.databases.create_float_attribute,
            "datetime": self.databases.create_datetime_attribute,
            "text": self.databases.create_text_attribute,
            "longtext": self.databases.create_longtext_attribute,
        }

        method = type_methods.get(type)
        if not method:
            raise ValueError(f"Unknown attribute type: {type}")

        return method(database_id=db_id, collection_id=collection_id, key=key, **kwargs)

    def create_index(self, db_id: str, collection_id: str, **kwargs):
        """Create an index in a collection."""
        return self.databases.create_index(database_id=db_id, collection_id=collection_id, **kwargs)
