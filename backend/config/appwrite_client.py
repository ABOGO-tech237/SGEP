# config/appwrite_client.py
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.messaging import Messaging
from appwrite.services.users import Users

from core.appwrite_utils import install_appwrite_get_body_shim


def _validate_appwrite_endpoint() -> None:
    endpoint = settings.APPWRITE_ENDPOINT or ""
    api_key = settings.APPWRITE_API_KEY or ""
    if not api_key:
        return
    if "<" in endpoint or "YOUR" in endpoint.upper():
        raise ImproperlyConfigured(
            "APPWRITE_ENDPOINT looks like a placeholder while APPWRITE_API_KEY is set. "
            "Set a real endpoint in backend/.env.local (see docs/appwrite-cloud-integration.md)."
        )


_validate_appwrite_endpoint()
install_appwrite_get_body_shim()

client = Client()
client.set_endpoint(settings.APPWRITE_ENDPOINT)
client.set_project(settings.APPWRITE_PROJECT_ID)
client.set_key(settings.APPWRITE_API_KEY)

databases = Databases(client)
users = Users(client)
messaging = Messaging(client)