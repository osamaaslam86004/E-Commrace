from boto3.s3.transfer import TransferConfig
from storages.backends.s3boto3 import (  # S3StaticStorage,
    S3Boto3Storage,
    S3ManifestStaticStorage,
)

GB = 1024 * 1024


class StaticStorage(S3ManifestStaticStorage):
    location = "static"
    default_acl = None
    file_overwrite = True  # Allows overwriting old static files
    transfer_config = TransferConfig(use_threads=False, multipart_threshold=5 * GB)


class PublicMediaStorage(S3Boto3Storage):
    # 1. Your PublicMediaStorage class should explicitly set the default_acl to "public-read" to allow direct access to files without signing.
    location = "media"
    default_acl = None
    file_overwrite = True
    transfer_config = TransferConfig(use_threads=False, multipart_threshold=5 * GB)
