import datetime
import json
import random
import secrets
import string
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

import bson
import pytest
from tests.v1.helpers.test_utils import get_async_repo, get_sync_repo, metastore_params

from arraylake.api_utils import ArraylakeHttpClient
from arraylake.metastore import MetastoreDatabase
from arraylake.repos.v1.repo import CollectionName, CommitID, NewCommit, Path, SessionID
from arraylake.types import DBID, NewRepoOperationStatus, OauthTokens, RepoOperationMode


@pytest.fixture(params=metastore_params)
def metastore_class_and_config(request):
    return request.param


@pytest.fixture()
async def new_sync_repo(isolated_org_name, chunkstore_bucket, user, metastore_class_and_config):
    repo_id = Helpers.random_repo_id()
    sync_repo = await get_sync_repo(chunkstore_bucket, repo_id, user, shared=False, org_name=isolated_org_name)
    return sync_repo


@pytest.fixture()
async def new_async_repo(isolated_org_name, chunkstore_bucket, user, metastore_class_and_config):
    repo_id = Helpers.random_repo_id()
    async_repo = await get_async_repo(chunkstore_bucket, repo_id, user, shared=False, org_name=isolated_org_name)
    return async_repo


@pytest.fixture()
async def metastore_database(metastore):
    repo_name = Helpers.random_repo_id()
    try:
        await metastore.delete_database(repo_name, imsure=True, imreallysure=True)
    except ValueError:
        pass  # repo doesn't exist yet
    return await metastore.create_database(repo_name)


class Helpers:
    """Helper functions for tests.

    This class is made available to tests using the helpers fixture.
    """

    @staticmethod
    def new_random_dbid() -> DBID:
        """Generate a random, 12 bytes database id"""
        return DBID(secrets.token_bytes(12))

    # __func__ is needed here for compatibility with Python < 3.10
    random_dbids: Iterator[DBID] = iter(new_random_dbid.__func__, None)
    """A fresh, infinite stream of random DBIDs"""

    @staticmethod
    def random_repo_id() -> str:
        return str(bson.ObjectId())

    @staticmethod
    def gen_docs(n, prefix="/some/path-") -> Mapping[Path, Mapping[str, Any]]:
        # make the generated items unique in some way
        rdm = str(uuid4())
        return {f"{prefix}{rdm}-{i}.json": {"i": i, "data": rdm} for i in range(n)}

    @staticmethod
    def gen_chunks(n, path="/some/path") -> Mapping[Path, Mapping[str, Any]]:
        # make the generated items unique in some way
        def coords():
            c0 = random.randint(0, 99999)
            c1 = random.randint(0, 99999)
            return f"c{c0}/{c1}"

        path = path.rstrip("/")
        return {f"{path}/{coords()}": {"uri": f"s3://testbucket/{uuid4()}"} for i in range(n)}

    @staticmethod
    def an_id(n: int) -> str:
        return "".join(random.choices(string.hexdigits, k=n))

    @staticmethod
    async def commit_session(db, session_id, parent_commit=None):
        commit_info = NewCommit(
            session_id=session_id,
            session_start_time=datetime.datetime.utcnow(),
            parent_commit=parent_commit,
            commit_time=datetime.datetime.utcnow(),
            author_name="Test Author",
            author_email="test@author.com",
            message=f"{Helpers.an_id(5)} commit",
        )
        return await db.new_commit(commit_info)

    @staticmethod
    async def make_commit(
        db: MetastoreDatabase,
        docs: Mapping[CollectionName, Mapping[Path, Mapping[str, Any]]],
        parent_commit: Optional[CommitID] = None,
    ):
        """Write some docs against a session + commit them"""

        _id = Helpers.an_id(5)
        session = SessionID(_id)
        for collection, ds in docs.items():
            await db.add_docs(ds, collection=collection, session_id=session, base_commit=parent_commit)
        commit_id = await Helpers.commit_session(db, session, parent_commit=parent_commit)
        return session, commit_id

    @staticmethod
    async def make_commits_to_branch(db, ncommits, ndocs, branch_name, overwrite_paths=False, parent_commit_id=None):
        """Utility to populate a branch with a commit history and docs"""
        commit_ids = []
        init_docs = Helpers.gen_docs(ndocs // 2, prefix=f"meta/root/")
        init_chunks = Helpers.gen_chunks(ndocs // 2, path=f"meta/root/")
        docs_created = []
        chunks_created = []
        for i in range(ncommits):
            docs = init_docs if overwrite_paths else Helpers.gen_docs(ndocs // 2, prefix=f"meta/root/{i}/")
            chunks = init_chunks if overwrite_paths else Helpers.gen_chunks(ndocs // 2, path=f"meta/root/{i}/")
            docs_created.append(docs)
            chunks_created.append(chunks)
            session, commit_id = await Helpers.make_commit(
                db, {CollectionName("metadata"): docs, CollectionName("chunks"): chunks}, parent_commit=parent_commit_id
            )
            await db.update_branch(
                branch_name,
                session_id=session,
                base_commit=parent_commit_id,
                new_commit=commit_id,
                new_branch=True if not parent_commit_id else False,
            )
            parent_commit_id = commit_id
            commit_ids.append(commit_id)
        return session, commit_ids, docs_created, chunks_created

    @staticmethod
    def oauth_tokens_from_file(file: Path) -> OauthTokens:
        """Utility to read an oauth tokens file"""
        with file.open() as f:
            return OauthTokens.model_validate_json(f.read())

    @staticmethod
    async def isolated_org(token, org_config):
        org_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        org_config["name"] = org_name
        client = ArraylakeHttpClient("http://localhost:8000", token=token)
        resp = await client._request("POST", "/orgs_test_create", content=json.dumps(org_config))
        return org_name

    @staticmethod
    async def set_repo_system_status(token, org_name, repo_name, mode: RepoOperationMode, message: str, is_user_modifiable: bool):
        """Util to set a system status for client tests.

        System statuses and the user modifiable status are not available in the public API.
        """
        client = ArraylakeHttpClient("http://localhost:8000", token=token)
        body = dict(NewRepoOperationStatus(mode=mode, message=message))
        resp = await client._request(
            "POST",
            "/repo_status_system",
            content=json.dumps(body),
            params={"org_name": org_name, "repo_name": repo_name, "is_user_modifiable": is_user_modifiable},
        )


@pytest.fixture(scope="session")
def helpers():
    """Provide the helpers found in the Helpers class"""
    return Helpers
