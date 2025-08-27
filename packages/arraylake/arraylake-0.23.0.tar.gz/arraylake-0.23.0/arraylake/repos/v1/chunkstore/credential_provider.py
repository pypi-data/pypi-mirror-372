import asyncio
from typing import Callable

from aiobotocore.credentials import AioRefreshableCredentials
from botocore.credentials import CredentialProvider

from arraylake.log_util import get_logger
from arraylake.types import S3Credentials

logger = get_logger(__name__)


class AutoRefreshingCredentialProvider(CredentialProvider):
    """Auto-refreshing credential provider for Aiobotocore.

    This provider fetches temporary credentials from an external source and
    refreshes them automatically when they are near expiration. This approach
    ensures the session always has valid credentials, even if they are short-lived.
    """

    def __init__(self, fetch_credentials_func: Callable[..., S3Credentials], advisory_timeout: int = 10 * 60):
        """
        Args:
            fetch_credentials_func:
                A function that fetches credentials. It should return a S3Credentials object.
            advisory_timeout:
                The number of seconds before the credentials expire to refresh them.
                Default is 10 minutes.
        """
        self.fetch_credentials_func = fetch_credentials_func
        self.advisory_timeout = advisory_timeout
        self._lock = asyncio.Lock()

    async def _refresh(self) -> dict[str, str]:
        """Fetch fresh credentials using the external function.
        Must return a dictionary of credentials metadata with
        keys: access_key, secret_key, token, expiry_time.
        """
        creds = await self.fetch_credentials_func()  # type: ignore

        return {
            "access_key": creds.aws_access_key_id,
            "secret_key": creds.aws_secret_access_key,
            "token": creds.aws_session_token,
            "expiry_time": creds.expiration.isoformat(),
        }

    async def load(self):
        """Load or refresh credentials as needed."""
        async with self._lock:
            metadata = await self._refresh()
            logger.debug("Loaded credentials: %s", metadata)
            return AioRefreshableCredentials.create_from_metadata(
                metadata=metadata,
                refresh_using=self._refresh,
                method="sts-assume-role",
                advisory_timeout=self.advisory_timeout,
            )
