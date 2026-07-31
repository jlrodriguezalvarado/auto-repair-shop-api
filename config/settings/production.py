from django.core.exceptions import ImproperlyConfigured
from .base import *  # noqa: F401,F403

def _required_env(name):
    value = env(name, default=None)  # noqa: F405
    if value is None or not str(value).strip():
        raise ImproperlyConfigured(
            f"The {name} environment variable is required in production."
        )
    return value

SECRET_KEY = _required_env("SECRET_KEY")
if SECRET_KEY.startswith("django-insecure") or len(SECRET_KEY) < 50:
    raise ImproperlyConfigured(
        "SECRET_KEY must be a unique value of at least 50 characters in production."
    )

JWT_SIGNING_KEY = _required_env("JWT_SIGNING_KEY")
SIMPLE_JWT["SIGNING_KEY"] = JWT_SIGNING_KEY  # noqa: F405

if env.bool("DEBUG", default=False):  # noqa: F405
    raise ImproperlyConfigured("DEBUG must be false in production.")
DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])  # noqa: F405
if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS must contain explicit hosts in production; '*' is forbidden."
    )

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])  # noqa: F405
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])  # noqa: F405
if not CORS_ALLOWED_ORIGINS:
    raise ImproperlyConfigured(
        "CORS_ALLOWED_ORIGINS must contain explicit frontend origins in production."
    )

if DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":  # noqa: F405
    raise ImproperlyConfigured("Production requires a PostgreSQL database configuration.")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SECURE_REDIRECT_EXEMPT = [r"^health/"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
