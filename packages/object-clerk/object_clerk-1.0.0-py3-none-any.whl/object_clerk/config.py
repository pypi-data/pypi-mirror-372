"""
Configuration parsing for the object clerk.

Environment variables containing object clerk configuration are retrieved
and parsed to establish defaults and precedence
"""

import json
import logging
from os import environ

from boto3.s3.transfer import TransferConfig
from botocore.config import Config as BotoConfig
from botocore.exceptions import ConnectionError
from botocore.exceptions import HTTPClientError

from object_clerk.exceptions import ObjectClerkServerInternalException
from object_clerk.exceptions import ObjectVerificationException

logger = logging.getLogger(__name__)

__all__ = [
    "CHECKSUM_RETRY_CONFIG",
    "CLIENT_CONFIG",
    "CONNECTION_RETRY_EXCEPTIONS",
    "MULTIPART_THRESHOLD",
    "UPLOAD_CONFIG",
    "CHECKSUM_RETRY_EXCEPTIONS",
]

MB_500 = 1024 * 1024 * 500  # 500 MB
MULTIPART_THRESHOLD = int(environ.get("MULTIPART_THRESHOLD", MB_500))

_s3_client_config = json.loads(
    environ.get(
        "S3_CLIENT_CONFIG",
        '{"connect_timeout": 60, "read_timeout": 60, "retries": {"max_attempts": 0}}',
    )
)
_s3_upload_config = json.loads(environ.get("S3_UPLOAD_CONFIG", "{}"))

# remove parameters controlled by MULTIPART_THRESHOLD if they exist
_multipart_config = dict(
    multipart_threshold=MULTIPART_THRESHOLD, multipart_chunksize=MULTIPART_THRESHOLD
)
_upload_config_with_multipart_override = {**_s3_upload_config, **_multipart_config}

UPLOAD_CONFIG = TransferConfig(**_upload_config_with_multipart_override)
CLIENT_CONFIG = BotoConfig(**_s3_client_config)

# Exceptions to retry according to the instance definition
CONNECTION_RETRY_EXCEPTIONS = (ConnectionError, HTTPClientError, ObjectClerkServerInternalException)

# Exceptions to retry when verifying checksums
CHECKSUM_RETRY_EXCEPTIONS = (ObjectVerificationException,)

# Set threshold at which the md5 checksum isn't valid to compare
# to the etag due to multipart uploads

CHECKSUM_RETRY_CONFIG = json.loads(environ.get("CHECKSUM_RETRY_CONFIG", "null")) or {
    "retry_delay": 1,
    "retry_backoff": 1,
    "retry_jitter": [1, 3],
    "retry_max_delay": 5,
    "retry_tries": 3,
}

logger.info(
    f"Object clerk configuration: "
    f"CHECKSUM_RETRY_CONFIG={CHECKSUM_RETRY_CONFIG}, "
    f"CONNECTION_RETRY_EXCEPTIONS={CONNECTION_RETRY_EXCEPTIONS}, "
    f"UPLOAD_CONFIG={UPLOAD_CONFIG}, "
    f"CLIENT_CONFIG={CLIENT_CONFIG}, "
    f"MULTIPART_THRESHOLD={MULTIPART_THRESHOLD}"
)
