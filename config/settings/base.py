"""Shared Django settings for auto-repair-shop-api."""
import logging
import os
from datetime import timedelta
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_path):
    environ.Env.read_env(env_path)

SECRET_KEY = env.str(
    "SECRET_KEY",
    default="django-insecure-5_)43y_rekea*+nlu^#k)6l70vu(x2eb0y+llpdso)_ebh=+j+",
)
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "django_filters",
    "corsheaders",
    "storages",
    "apps.common",
    "apps.users",
    "apps.company",
    "apps.customers",
    "apps.vehicles",
    "apps.catalog",
    "apps.work_orders",
    "apps.estimates",
    "apps.receipts",
    "apps.dashboard",
    "apps.notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

def _database_from_env():
    database_url = env.str("DATABASE_URL", default="")
    if database_url:
        return env.db("DATABASE_URL")
    name = env.str("POSTGRES_DB", default=env.str("DB_NAME", default=""))
    user = env.str("DB_USER", default="")
    password = env.str("DB_PASSWORD", default="")
    host = env.str("DB_HOST", default="")
    port = env.str("DB_PORT_INTERNAL", default=env.str("DB_PORT", default="5432"))
    if name and user and host:
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": name,
            "USER": user,
            "PASSWORD": password,
            "HOST": host,
            "PORT": port,
        }
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }

DATABASES = {"default": _database_from_env()}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# AWS S3 Settings (optional — local FileSystemStorage when unset)
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default=None)
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default=None)
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default=None)
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default=None)
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default=None) or None
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_ADDRESSING_STYLE = "virtual"
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 3600
# Base key prefix inside the bucket (per environment: local/dev/prod, etc.)
AWS_S3_KEY_PREFIX = env("AWS_S3_KEY_PREFIX", default="")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    # django-storages uses AWS_LOCATION as the base prefix for all S3 paths.
    AWS_LOCATION = AWS_S3_KEY_PREFIX
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    }

AUTH_USER_MODEL = "users.User"
# Username uniqueness is enforced via partial UniqueConstraint (alive rows only).
SILENCED_SYSTEM_CHECKS = ["auth.E003"]
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "apps.users.authentication.UserAwareJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": env.str("JWT_SIGNING_KEY", default=SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
}
SPECTACULAR_SETTINGS = {
    "TITLE": "App Taller Mecánico API",
    "DESCRIPTION": "API para la gestión de un taller mecánico.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "APPEND_COMPONENTS": {
        "parameters": {
            "CompanyContextHeader": {
                "name": "X-Company-Id",
                "in": "header",
                "required": False,
                "schema": {"type": "integer"},
                "description": (
                    "SUPER_ADMIN read-only company context. "
                    "Required for SUPER_ADMIN on tenant business GET endpoints."
                ),
            }
        }
    },
}
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=True)
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-company-id",
]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Web Push (VAPID) for PWA notifications — HTTPS required in production.
def _load_web_push_vapid_private_key():
    logger = logging.getLogger(__name__)
    key_file = env("WEB_PUSH_VAPID_PRIVATE_KEY_FILE", default=None)
    if key_file:
        key_path = key_file if os.path.isabs(key_file) else os.path.join(BASE_DIR, key_file)
        if os.path.isfile(key_path):
            return key_path
        logger.error("WEB_PUSH_VAPID_PRIVATE_KEY_FILE does not exist: %s", key_path)
    inline_key = env("WEB_PUSH_VAPID_PRIVATE_KEY", default="")
    if inline_key:
        return inline_key.replace("\\n", "\n").strip()
    return ""

WEB_PUSH_VAPID_PUBLIC_KEY = env("WEB_PUSH_VAPID_PUBLIC_KEY", default="")
WEB_PUSH_VAPID_PRIVATE_KEY = _load_web_push_vapid_private_key()
WEB_PUSH_VAPID_SUBJECT = env("WEB_PUSH_VAPID_SUBJECT", default="mailto:admin@example.com")
