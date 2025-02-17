from boto3.s3.transfer import TransferConfig
from storages.backends.s3boto3 import S3ManifestStaticStorage, S3StaticStorage

GB = 1024 * 1024


class StaticStorage(S3StaticStorage):
    location = "static"
    default_acl = None
    file_overwrite = True  # Allows overwriting old static files
    transfer_config = TransferConfig(use_threads=False, multipart_threshold=1 * GB)


class PublicMediaStorage(S3ManifestStaticStorage):
    # 1. Your PublicMediaStorage class should explicitly set the default_acl to "public-read" to allow direct access to files without signing.
    location = "media"
    default_acl = None
    file_overwrite = False
    transfer_config = TransferConfig(use_threads=False, multipart_threshold=1 * GB)
