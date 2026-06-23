from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        from core import checks  # noqa: F401
        from core.appwrite_utils import install_appwrite_get_body_shim

        install_appwrite_get_body_shim()
