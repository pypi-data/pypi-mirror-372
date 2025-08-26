from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from importlib import import_module

USE_KEYCLOAK = getattr(settings, "USE_KEYCLOAK", False)


KEYCLOAK_POST_LOGOUT_URL = getattr(settings, "KEYCLOAK_POST_LOGOUT_URL")
REALM_NAME = getattr(settings, "REALM_NAME")
CLIENT_ID = getattr(settings, "CLIENT_ID")
KEYCLOAK_URL_BASE_CLIENT = getattr(settings, "KEYCLOAK_URL_BASE_CLIENT")
KEYCLOAK_SCOPES = getattr(settings, "KEYCLOAK_SCOPES")
KEYCLOAK_REDIRECT_URI = getattr(settings, "KEYCLOAK_REDIRECT_URI")
CLIENT_SECRET = getattr(settings, "CLIENT_SECRET")
KEYCLOAK_URL_BASE = getattr(settings, "KEYCLOAK_URL_BASE")
KEYCLOAK_AUDIENCE = getattr(settings, "KEYCLOAK_AUDIENCE")
KEYCLOAK_IS_CREATE = getattr(settings, "KEYCLOAK_IS_CREATE", True)
KEYCLOAK_CERT_FILENAME = getattr(
    settings, "KEYCLOAK_CERT_FILENAME", "/home/sdl/cert/host.pem"
)
AUTH_PAGE_DOCUMENT = getattr(settings, "AUTH_PAGE_DOCUMENT")
ERROR_PAGE_DOCUMENT = getattr(settings, "ERROR_PAGE_DOCUMENT")

VERSION_TAG = getattr(settings, "VERSION_TAG")

DEFAULT_REDIRECT_URI = getattr(settings, "DEFAULT_REDIRECT_URI", "/")


def get_custom_callback(name: str):
    path = getattr(settings, name, None)
    if path is None:
        return None
    module_name, func_name = path.rsplit(".", 1)
    module = import_module(module_name)
    return getattr(module, func_name)


CACHE_CALLBACK = get_custom_callback("CACHE_CALLBACK")
CLEAR_CACHE_CALLBACK = get_custom_callback("CLEAR_CACHE_CALLBACK")


if USE_KEYCLOAK and not (
    CLIENT_ID is not None
    and CLIENT_SECRET is not None
    and REALM_NAME is not None
    and KEYCLOAK_URL_BASE is not None
    and KEYCLOAK_POST_LOGOUT_URL is not None
    and KEYCLOAK_REDIRECT_URI is not None
    and KEYCLOAK_IS_CREATE is not None
):
    raise ImproperlyConfigured(
        "Could not find one of KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET, KEYCLOAK_REALM_NAME, KEYCLOAK_URL_BASE, KEYCLOAK_POST_LOGOUT_URL in environment"
    )
