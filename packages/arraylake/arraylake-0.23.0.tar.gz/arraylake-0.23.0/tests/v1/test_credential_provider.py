from datetime import datetime, timedelta

import pytest
from aiobotocore.credentials import AioRefreshableCredentials
from dateutil.tz import tzlocal

from arraylake.repos.v1.chunkstore.credential_provider import (
    AutoRefreshingCredentialProvider,
)
from arraylake.types import S3Credentials


async def mock_fetcher(delta_min: int = 60) -> S3Credentials:
    """Mock credential fetcher for testing.

    Default expiration is 60 minutes from now.
    """
    return S3Credentials(
        aws_access_key_id="access_key",
        aws_secret_access_key="secret_key",
        aws_session_token="session_token",
        expiration=datetime.now(tzlocal()) + timedelta(minutes=delta_min),
    )


async def test_credential_provider_refresh():
    cred_provider = AutoRefreshingCredentialProvider(mock_fetcher)
    creds = await cred_provider._refresh()
    assert creds["access_key"] == "access_key"
    assert creds["secret_key"] == "secret_key"
    assert creds["token"] == "session_token"
    assert "expiry_time" in creds  # can't compare exact time


async def test_credential_provider_load():
    cred_provider = AutoRefreshingCredentialProvider(mock_fetcher, advisory_timeout=10 * 60)
    refreshable_creds = await cred_provider.load()
    assert isinstance(refreshable_creds, AioRefreshableCredentials)
    creds = await refreshable_creds.get_frozen_credentials()
    assert creds.access_key == "access_key"
    assert creds.secret_key == "secret_key"
    assert creds.token == "session_token"
    assert refreshable_creds.refresh_needed() is False


async def test_credential_provider_refresh_expired_creds():
    fetch_credentials_func = lambda: mock_fetcher(delta_min=0)
    cred_provider = AutoRefreshingCredentialProvider(fetch_credentials_func, advisory_timeout=2)
    refreshable_creds = await cred_provider.load()
    assert isinstance(refreshable_creds, AioRefreshableCredentials)
    assert refreshable_creds.refresh_needed(refresh_in=2) is True
    # Check that credentials are refreshed
    # This will raise a RuntimeError because the refreshed credentials will expire immediately
    # But the refresh is successful
    with pytest.raises(RuntimeError) as excinfo:
        await refreshable_creds.get_frozen_credentials()
    assert "Credentials were refreshed, but the refreshed credentials are still expired." in str(excinfo.value)
