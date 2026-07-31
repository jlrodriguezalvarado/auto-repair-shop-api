from __future__ import annotations

import boto3
from botocore.config import Config
from django.conf import settings
from django.core.files.storage import default_storage


def is_s3_storage() -> bool:
    bucket_name = getattr(default_storage, "bucket_name", None) or getattr(
        settings, "AWS_STORAGE_BUCKET_NAME", None
    )
    return bool(bucket_name)


def storage_object_key(storage_name: str) -> str:
    location = getattr(default_storage, "location", "") or ""
    object_key = storage_name.lstrip("/")
    if location:
        object_key = f"{location.rstrip('/')}/{object_key.lstrip('/')}"
    return object_key


def _s3_client():
    aws_region = getattr(settings, "AWS_S3_REGION_NAME", None) or "us-east-1"
    endpoint_url = getattr(settings, "AWS_S3_ENDPOINT_URL", None) or None
    session = boto3.session.Session(
        aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None) or None,
        aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None) or None,
        region_name=aws_region,
    )
    return session.client(
        "s3",
        endpoint_url=endpoint_url,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "virtual"},
        ),
    )


def generate_presigned_get_url(
    storage_name: str,
    *,
    expires_in_seconds: int | None = None,
) -> str | None:
    if not storage_name:
        return None
    bucket_name = getattr(default_storage, "bucket_name", None) or getattr(
        settings, "AWS_STORAGE_BUCKET_NAME", None
    )
    if not bucket_name:
        return default_storage.url(storage_name)
    if expires_in_seconds is None:
        expires_in_seconds = int(getattr(settings, "AWS_QUERYSTRING_EXPIRE", 3600))
    return _s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": storage_object_key(storage_name)},
        ExpiresIn=expires_in_seconds,
    )


def presigned_url_for_file_field(file_field, *, expires_in_seconds: int | None = None) -> str:
    if not file_field:
        return ""
    return generate_presigned_get_url(file_field.name, expires_in_seconds=expires_in_seconds) or ""
