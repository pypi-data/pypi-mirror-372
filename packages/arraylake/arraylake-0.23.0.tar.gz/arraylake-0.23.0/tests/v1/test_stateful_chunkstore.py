from uuid import uuid4

import botocore
import hypothesis
import hypothesis.strategies as st
import pytest
from hypothesis import note
from hypothesis.stateful import (
    HealthCheck,
    RuleBasedStateMachine,
    Settings,
    initialize,
    precondition,
    rule,
    run_state_machine_as_test,
)

from arraylake.asyn import sync
from arraylake.exceptions import ExpectedChunkNotFoundError
from arraylake.repos.v1.chunkstore import *
from arraylake.repos.v1.types import *
from arraylake.types import *


class HashableReferenceData(ReferenceData):
    """Will be used as keys for the dict chunkstore that we use as a model."""

    def __hash__(self):
        return hash((self.uri, self.offset, self.length, self.hash["method"], self.hash["token"], self.v, self.sid))


class Model:
    def __init__(self, **kwargs):
        self.store = {}
        self.session = None
        self.changes_made = True

    def new_session(self, session_id: SessionID):
        self.changes_made = False
        self.session = session_id

    def has_session(self) -> bool:
        return self.session is not None

    def get_session(self) -> SessionID:
        return self.session

    def has_chunks(self) -> bool:
        return len(self.store) > 0

    def num_chunks(self) -> int:
        return len(self.store)

    def get_chunk(self, index):
        references = list(self.store.keys())
        reference = references[index]
        data = self.store[reference]
        return (ReferenceData(**reference.dict()), data)

    def add_chunk(self, reference: ReferenceData, data: bytes) -> ReferenceData:
        reference = HashableReferenceData(**reference.dict())
        self.store[reference] = data
        self.changes_made = True

        return reference


sessions = st.from_regex(r"[a-f0-9]{12}", fullmatch=True).map(lambda s: SessionID(s))
chunk_hash = st.from_regex(r"[a-f0-9]{32}", fullmatch=True).map(lambda s: ChunkHash(method="hashlib.sha256", token=s))
chunk_bytes = st.binary(min_size=1, max_size=100)


@st.composite
def reference_st(draw) -> ReferenceData:
    session_id = draw(sessions)
    hash = draw(chunk_hash)
    return ReferenceData(uri=None, sid=session_id, v=ChunkstoreSchemaVersion.V1, offset=0, length=100, hash=hash)


@pytest.mark.slow
def test_v1_chunkstore():
    class ChunkstoreV1StatefulTest(RuleBasedStateMachine):
        @initialize()
        def init(self):
            note("----------")
            self.model = Model()
            bucket = Bucket(
                id=uuid4(), nickname="test", platform="s3", name="testbucket", extra_config={"endpoint_url": "http://localhost:9000"}
            )
            self.chunkstore = mk_chunkstore_from_bucket_config(bucket=bucket, repo_id=DBID(uuid4().bytes))

        @rule(data=st.data())
        @precondition(lambda self: self.model and self.model.has_chunks())
        def get_existing_chunk(self, data):
            note("Getting existing chunk")
            num_chunks = self.model.num_chunks()
            index = data.draw(st.integers(0, num_chunks - 1))
            reference, chunk_data = self.model.get_chunk(index)
            store_data = sync(self.chunkstore.get_chunk, chunk_ref=reference)
            assert len(store_data) == len(chunk_data)
            assert store_data == chunk_data

        @rule(data=chunk_bytes)
        @precondition(lambda self: self.model and self.model.has_session())
        def add_chunk(self, data):
            note("Adding new chunk")
            hash_method = "hashlib.sha256"
            ref = sync(self.chunkstore.add_chunk, data=data, session_id=self.model.get_session(), hash_method=hash_method)
            self.model.add_chunk(ref, data)

        @rule(session_id=sessions)
        @precondition(lambda self: self.model and self.model.changes_made)
        def change_session(self, session_id):
            note("Starting new session")
            self.model.new_session(session_id)

        @rule(reference=reference_st())
        def get_nonexistent_chunk(self, reference):
            note("Getting nonexistent chunk")
            with pytest.warns(UserWarning, match="failed to fetch chunk"):
                with pytest.raises(ExpectedChunkNotFoundError):
                    sync(self.chunkstore.get_chunk, chunk_ref=reference)

    settings = Settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    run_state_machine_as_test(ChunkstoreV1StatefulTest, settings=settings)
