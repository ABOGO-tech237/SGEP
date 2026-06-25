from django.core.checks import Warning, register
from django.conf import settings


@register()
def check_appwrite_endpoint(app_configs, **kwargs):
    endpoint = settings.APPWRITE_ENDPOINT or ""
    if "<" in endpoint or "YOUR" in endpoint.upper():
        return [
            Warning(
                "APPWRITE_ENDPOINT looks like a placeholder. "
                "Copy real Appwrite values to backend/.env.local for local development.",
                id="core.W001",
            )
        ]
    return []
