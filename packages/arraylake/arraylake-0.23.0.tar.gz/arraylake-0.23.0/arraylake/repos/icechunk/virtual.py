from typing import Callable

from arraylake.repos.icechunk.utils import _raise_if_no_icechunk
from arraylake.types import GSCredentials, S3Credentials


def get_icechunk_container_credentials(
    bucket_platform: str,
    credentials: S3Credentials | GSCredentials | None,
    credential_refresh_func: Callable | None,
):
    """Gets the icechunk virtual chunk container credentials
    from the given bucket config and credentials.

    Args:
        bucket_platform: The platform of the bucket. Supported platforms are "s3", "s3c", and "minio".
        credentials: Optional S3Credentials or GSCredentials to use for the virtual chunk container.
        credential_refresh_func (Callable[[], S3StaticCredentials | GcsBearerCredential]):
            Optional function to refresh S3 or GCS credentials. This function must
            be synchronous, cannot take in any args, and return a
            icechunk.S3StaticCredentials or icechunk.GcsBearerCredential object.

    Returns:
        icechunk.Credentials.S3:
            The virtual chunk container credentials for the bucket.
    """
    _raise_if_no_icechunk()
    import icechunk

    if credential_refresh_func and credentials:
        raise ValueError("Cannot provide both static credentials and a credential refresh function.")

    # Check the if the bucket is an S3 or S3-compatible bucket
    if bucket_platform in ("s3", "s3c", "s3-compatible", "minio"):
        if credential_refresh_func:
            return icechunk.s3_refreshable_credentials(credential_refresh_func)
        elif credentials:
            assert isinstance(credentials, S3Credentials)
            return icechunk.s3_static_credentials(
                access_key_id=credentials.aws_access_key_id,
                secret_access_key=credentials.aws_secret_access_key,
                session_token=credentials.aws_session_token,
                expires_after=credentials.expiration,
            )
        else:
            return icechunk.s3_from_env_credentials()
    elif bucket_platform in ("gs"):
        # TODO: Implement when refreshable GCS credentials are supported
        # https://github.com/earth-mover/icechunk/pull/776
        if credentials:
            assert isinstance(credentials, GSCredentials)
            return icechunk.GcsBearerCredential(bearer=credentials.access_token, expires_after=credentials.expiration)
    else:
        raise ValueError(f"Unsupported bucket platform for virtual chunk container credentials: {bucket_platform}")
