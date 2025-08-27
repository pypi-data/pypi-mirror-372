import asyncio
import pickle
from datetime import datetime, timedelta

import pytest
from tests.v1.helpers.test_utils import get_async_repo, get_sync_repo

from arraylake import config
from arraylake.repos.v1.repo import LocalWriteSession, as_write_session


@pytest.mark.asyncio
async def test_sessions_distributed_workflow(chunkstore_bucket, user, helpers):
    """A test of the shared-nothing distributed workflow."""
    with config.set({"server_managed_sessions": True}):
        repo_id = helpers.random_repo_id()
        coordinator = await get_sync_repo(chunkstore_bucket, repo_id, user, shared=False)

        # Initiate a session
        session = coordinator.create_session(expires_in=timedelta(hours=1), message="testing dist session")

        # Write a top-level doc
        coordinator._set_doc("/global.json", content={"foo": 1, "bar": 2})

        # Define a distributed write job
        async def dist_write(worker_id, session_id):
            worker = await get_sync_repo(chunkstore_bucket, repo_id, user, shared=True)
            worker.join_session(session_id)
            key = f"/foo/c0/1/{worker_id}"
            data = f"0000000{worker_id}".encode()
            worker._set_chunk(key, data=data)

        # Spawn N concurrent writers and write jobs
        num_concurrent_jobs = 5
        jobs = [dist_write(id, session.id) for id in range(num_concurrent_jobs)]
        _ = await asyncio.gather(*jobs)

        # Commit from the coordinator
        coordinator.commit("finished testing dist session")

        # Validate all the data was written
        assert coordinator._get_doc("/global.json") == {"foo": 1, "bar": 2}
        for worker_id in range(5):
            key = f"/foo/c0/1/{worker_id}"
            data = f"0000000{worker_id}".encode()
            assert coordinator._get_chunk(key) == data


@pytest.mark.asyncio
async def test_sessions_mixed_workflow(chunkstore_bucket, user, helpers):
    """A test of a mixed workflow, where a single instance creates the session
    and its serialized clones interact without explicitly using session verbs.
    This mimics a Dask-like, shared state concurrency model."""
    with config.set({"server_managed_sessions": True}):
        repo_id = helpers.random_repo_id()
        repo = await get_sync_repo(chunkstore_bucket, repo_id, user, shared=False)
        repo.checkout(expires_in=timedelta(hours=1))

        # Define a distribute write job
        async def dist_write(pickled_repo, segment):
            repo = pickle.loads(pickled_repo)
            key = f"/foo/c0/1/{segment}"
            data = f"0000000{segment}".encode()
            repo._set_chunk(key, data=data)

        # Spawn N concurrent writers and write jobs
        num_concurrent_jobs = 5
        _ = await asyncio.gather(*[dist_write(pickle.dumps(repo), id) for id in range(num_concurrent_jobs)])

        # Commit
        repo.commit("finished testing mixed session")

        # Validate all data was written
        for worker_id in range(5):
            key = f"/foo/c0/1/{worker_id}"
            data = f"0000000{worker_id}".encode()
            assert repo._get_chunk(key) == data


@pytest.mark.asyncio
async def test_sessions_expiration(chunkstore_bucket, user, helpers):
    with config.set({"server_managed_sessions": True}):
        repo_id = helpers.random_repo_id()
        repo = await get_async_repo(chunkstore_bucket, repo_id, user, shared=False)

        # Validate we prevent creating sessions with unreasonable expiration times.
        with pytest.raises(ValueError, match="Max expiry exceeded"):
            session = await repo.create_session(expires_in=timedelta(days=1000))

        with pytest.raises(ValueError, match="Max expiry exceeded"):
            session = await repo.create_session(expires_in=timedelta(minutes=1))
            assert isinstance(session, LocalWriteSession)
            await as_write_session(repo.session).update_expiration(expires_in=timedelta(days=1000))

        # Validate we prevent clients from acquiring expired sessions
        session = await repo.create_session(expires_in=timedelta(minutes=1))
        assert isinstance(session, LocalWriteSession)
        backdated_session = await as_write_session(repo.session).update_expiration(expires_in=timedelta(hours=-1))
        assert backdated_session.id == session.id
        with pytest.raises(ValueError, match="Session expired"):
            await repo.join_session(session.id)

        # Validate we can't write to sessions that have expired.
        session = await repo.create_session(expires_in=timedelta(minutes=1))

        # Set the expiration to the past
        assert isinstance(session, LocalWriteSession)
        updated_session = await as_write_session(repo.session).update_expiration(expires_in=timedelta(hours=-1))

        # Assert the updated session is the same as the original, bar the
        # expiration date
        assert updated_session.id == session.id
        assert updated_session.expiration < datetime.utcnow()
        with pytest.raises(ValueError, match="Session expired"):
            # Throw exception when we try to write
            await repo._set_doc("/foo.json", content={"foo": 1})

        # Validate we can't write to sessions that have explicitly been abandoned.
        session = await repo.create_session(expires_in=timedelta(minutes=1))

        # Explicitly abandon the session
        assert isinstance(session, LocalWriteSession)
        updated_session = await as_write_session(repo.session).abandon()

        assert updated_session.id == session.id
        assert updated_session.expiration < datetime.utcnow()

        with pytest.raises(ValueError, match="Session expired"):
            await repo._set_doc("/foo.json", content={"foo": 1})

        # Validate that we can't write to sessions that have expired.
        session = await repo.create_session(expires_in=timedelta(seconds=0.1))

        # Sleep past the expiration
        await asyncio.sleep(0.11)

        assert isinstance(session, LocalWriteSession)
        assert as_write_session(session).expiration < datetime.utcnow()
        with pytest.raises(ValueError, match="Session expired"):
            await repo._set_doc("/foo.json", content={"foo": 1})


async def test_sessions_read_only_sessions(chunkstore_bucket, user, helpers):
    """Ensure that write verbs won't work from a LocalReadSession."""
    with config.set({"server_managed_sessions": True}):
        repo_id = helpers.random_repo_id()
        repo = await get_sync_repo(chunkstore_bucket, repo_id, user, shared=False)
        repo.checkout(for_writing=False)

        with pytest.raises(OSError, match="Repo is not writable"):
            repo._set_doc("/pacific.json", content={"foo": 1, "bar": 2})

        with pytest.raises(OSError, match="Repo is not writable"):
            repo._del_doc("/foo.json")

        with pytest.raises(OSError, match="Repo is not writable"):
            repo._rename("/foo.json", "/bar.json")

        repo.checkout(for_writing=True)
        repo._set_doc("/pacific.json", content={"foo": 1, "bar": 2})
        commit_0 = repo.commit("first commit", checkout_for_writing=False)

        assert repo._get_doc("/pacific.json") == {"foo": 1, "bar": 2}

        with pytest.raises(OSError, match="Repo is not writable"):
            repo._set_doc("/pacific.json", content={"foo": 2, "bar": 1})


async def test_sessions_fails_when_disabled(chunkstore_bucket, user, helpers):
    """Ensure that clients who have not opted in to server-managed sessions
    cannot use the verbs."""
    with config.set({"server_managed_sessions": True}):
        repo_id = helpers.random_repo_id()
        enabled_client = await get_sync_repo(chunkstore_bucket, repo_id, user, shared=False)
        active_server_session = enabled_client.create_session()

        with config.set({"server_managed_sessions": False}):
            disabled_client = await get_sync_repo(chunkstore_bucket, repo_id, user, shared=True)

            with pytest.raises(ValueError, match="Joining sessions not supported"):
                disabled_client.join_session(active_server_session.id)

            with pytest.raises(ValueError, match="Joining sessions not supported"):
                disabled_client.checkout(session_token=active_server_session.id)

            with pytest.raises(ValueError, match="Joining sessions not supported"):
                local_session = disabled_client.create_session()
                enabled_client.join_session(local_session.id)


@pytest.mark.flaky(retries=3, delay=1)
async def test_sessions_list_active_sessions(chunkstore_bucket, user, helpers):
    """Ensure that we can list active sessions."""
    # TODO: Remove this once managed sessions are mandatory.
    with config.set({"server_managed_sessions": True}):

        def just_ids(sessions):
            return [session.id for session in sessions]

        repo_id = helpers.random_repo_id()
        repo = await get_sync_repo(chunkstore_bucket, repo_id, user, shared=False)

        # Create a session and verify that it appears in list_active_sessions
        session_a = repo.create_session(expires_in=timedelta(seconds=120)).id
        sessions = just_ids(repo.list_active_sessions())
        assert session_a in set(sessions)

        # Create a session that expires in 2 seconds.
        session_b = repo.create_session(expires_in=timedelta(seconds=0.5)).id

        start = datetime.utcnow()
        while (datetime.utcnow() - start).total_seconds() < 30:
            sessions = just_ids(repo.list_active_sessions())
            sessions_set = set(sessions)
            if session_b not in sessions_set:
                # the session expired and left the list of active sessions
                return
            await asyncio.sleep(0.1)

        # we waited 30 seconds but the session never expired
        assert False, "Session should expire"
