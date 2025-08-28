from django.conf import settings

DEFAULTS = {
    "ALLOW_REGISTRATION": True, #Default settings , kan je aanpassen, geen hardcoded values in de views zelf
    "LOGIN_WITH_EMAIL": True,
    "ENABLE_JWT": False,
    "ENABLE_BLACKLIST_UI": True,
    "BASE_TEMPLATE": "tlcc_auth/base_auth.html",
    "POST_LOGIN_REDIRECT": "/",
    "POST_LOGOUT_REDIRECT": "/",
}

def get(name):
    return getattr(settings, "TLCC_AUTH", {}).get(name, DEFAULTS[name])
