import pytest
from arraylake_mongo_metastore import MongoMetastoreConfig, MongoSessionedMetastore

from arraylake.api_utils import ArraylakeHttpClient
from arraylake.metastore import HttpMetastore, HttpMetastoreConfig
from arraylake.repos.v1.repo import AsyncRepo, Repo

ORG = "default"
SERVICE_URI = "http://localhost:8000"
MONGO_URI = "mongodb://localhost:27017/mongodb"
DEFAULT_TOKEN = "test-token"

# NOTE: The following fixture parameters correspond to the
# metastore_class_and_config() fixture in conftest.py. Consumers of that fixture
# expect a tuple of three values:
#
#   (<Metastore class>, <Metastore config>, <use_sessions boolean>)

# Parameters used for repo fixtures
metastore_params = [
    pytest.param(
        (MongoSessionedMetastore, MongoMetastoreConfig(MONGO_URI, managed_sessions=False)),
        id="mongo",
    ),
    pytest.param((HttpMetastore, HttpMetastoreConfig(SERVICE_URI, ORG, DEFAULT_TOKEN, managed_sessions=False)), id="api"),
]

# Parameters used to override repo fixtures, flagging HttpMetastore as slow
# Usage: @pytest.mark.parametrize('metastore_class_and_config', metastore_params_http_slow)
metastore_params_http_slow = [
    pytest.param(
        (MongoSessionedMetastore, MongoMetastoreConfig(MONGO_URI, managed_sessions=False)),
        id="mongo",
    ),
    pytest.param(
        (HttpMetastore, HttpMetastoreConfig(SERVICE_URI, ORG, DEFAULT_TOKEN, managed_sessions=False)), id="api", marks=pytest.mark.slow
    ),
]

# Parameters used to override repo fixtures, getting MongoMetastore only
# Usage: @pytest.mark.parametrize('metastore_class_and_config', metastore_params_only_mongo)
metastore_params_only_mongo = [
    pytest.param(
        (MongoSessionedMetastore, MongoMetastoreConfig(MONGO_URI, managed_sessions=False)),
        id="mongo",
    ),
]

# Parameters used to override repo fixtures, getting managed-sessions-enabled Metastores
# Usage: @pytest.mark.parametrize('metastore_class_and_config', metastore_params_sessions)
metastore_params_sessions = [
    pytest.param(
        (MongoSessionedMetastore, MongoMetastoreConfig(MONGO_URI, managed_sessions=True)),
        id="mongo-sessions",
    ),
    pytest.param((HttpMetastore, HttpMetastoreConfig(SERVICE_URI, ORG, DEFAULT_TOKEN, managed_sessions=True)), id="api-sessions"),
]

# Parameters used to override repo fixtures, getting MongoMetastore pointing to port 27018 only
# Usage: @pytest.mark.parametrize('metastore_class_and_config', metastore_params_only_mongo)
metastore_params_only_mongo_27018 = [
    pytest.param((MongoSessionedMetastore, MongoMetastoreConfig("mongodb://localhost:27018/mongodb", managed_sessions=False)), id="mongo"),
]

# NOTE: The following utility functions are shamelessly cribbed almost verbatim
# from conftest.py. They are here because we desire greater flexibility and
# reusability in test setup. Concretely, we need to initialize repos (and
# therefore, metastores) with different client config within the same test,
# which is not possible from within our current fixture setup.


def get_api_metastore(org: str = ORG, token: str = DEFAULT_TOKEN):
    """Instantiate an HttpMetastore for API client testing."""
    return HttpMetastore(HttpMetastoreConfig(SERVICE_URI, org, token))


async def get_new_api_metastore_database(metastore, repo_name: str):
    """Obtain a new MetastoreDatabase instance. This will destroy any pre-existing
    databases that share the same name, so this should only be called once for a
    given test."""
    try:
        await metastore.delete_database(repo_name, imsure=True, imreallysure=True)
    except ValueError:
        pass  # repo doesn't exist yet
    return await metastore.create_database(repo_name)


async def get_shared_api_metastore_database(metastore, repo_name: str):
    """Obtain a new MetastoreDatabase *without* first deleting any identically-named
    databases. This is useful for e.g. instantiating multiple clients within a
    given test, each of which will query a shared database."""
    return await metastore.open_database(repo_name)


async def get_metastoredb(org_name, repo_name, shared):
    """Obtain a new MetastoreDatabase to test against."""
    metastore = get_api_metastore(org_name) if org_name else get_api_metastore()
    # Ensure the org has v1-write feature flag
    org_to_use = org_name if org_name else ORG
    await ensure_org_v1_write_flag(org_to_use)
    if shared:
        metastore_db = await get_shared_api_metastore_database(metastore, repo_name=repo_name)
    else:
        metastore_db = await get_new_api_metastore_database(metastore, repo_name=repo_name)
    return metastore_db


async def ensure_org_v1_write_flag(org_name):
    """Ensure the specified org has a v1-write feature flag."""
    client = ArraylakeHttpClient(SERVICE_URI, token=DEFAULT_TOKEN)
    response = await client._request("PATCH", f"/orgs/{org_name}", json={"add_feature_flag": "v1-write"})

    if response.status_code != 200:
        raise ValueError(f"Failed to ensure org {org_name} has v1-write flag")


async def get_sync_repo(chunkstore_bucket, repo_id: str, user, shared, org_name=None) -> Repo:
    """Obtain a sync Repo instance. If shared=True, this function will assume the
    caller does not want data isolation (i.e. deleting any pre-existing
    databases)."""
    metastore_db = await get_metastoredb(org_name, repo_id, shared)
    return Repo.from_metastore_and_chunkstore(metastore_db=metastore_db, chunkstore=chunkstore_bucket, name=repo_id, author=user)


async def get_async_repo(chunkstore_bucket, repo_id: str, user, shared, org_name=None) -> AsyncRepo:
    """Obtain an AsyncRepo instance. If shared=True, this function will assume the
    caller does not want data isolation (i.e. deleting any pre-existing
    databases)."""
    metastore_db = await get_metastoredb(org_name, repo_id, shared)
    repo = AsyncRepo(metastore_db=metastore_db, chunkstore=chunkstore_bucket, name=repo_id, author=user)
    return repo
