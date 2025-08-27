import json
from datetime import datetime
from typing import NewType

from icechunk import Diff, SnapshotInfo
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer
from zarr import AsyncArray, AsyncGroup
from zarr.abc.metadata import Metadata

try:
    # TODO: remove this import when we drop support for Zarr<3.1
    from zarr.core.metadata.v3 import V3JsonEncoder
except ImportError:
    V3JsonEncoder = None

from arraylake.types import datetime_to_isoformat

CommitId = NewType("CommitId", str)
TagName = NewType("TagName", str)
BranchName = NewType("BranchName", str)


class Commit(BaseModel):
    id: CommitId = Field(alias="_id")
    message: str
    commit_time: datetime
    parent_id: CommitId | None = None
    author_name: str | None = None
    author_email: EmailStr | None = None
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    @classmethod
    def from_snapshot(cls, snapshot: SnapshotInfo) -> "Commit":
        return cls(
            _id=CommitId(snapshot.id),
            message=snapshot.message,
            commit_time=snapshot.written_at,
            author_name=snapshot.metadata.get("author_name"),
            author_email=snapshot.metadata.get("author_email"),
            parent_id=CommitId(snapshot.parent_id) if snapshot.parent_id else None,
        )

    @field_serializer("commit_time")
    def serialize_commit_time(self, commit_time: datetime) -> str:
        return datetime_to_isoformat(commit_time)


class CommitDiff(BaseModel):
    from_commit_id: CommitId | None
    to_commit_id: CommitId
    new_groups: list[str]
    new_arrays: list[str]
    deleted_groups: list[str]
    deleted_arrays: list[str]
    updated_groups: list[str]
    updated_arrays: list[str]
    updated_chunks: dict[str, int]

    @classmethod
    def from_diff(cls, from_commit_id: str | None, to_commit_id: str, diff: Diff | None) -> "CommitDiff":
        if diff is None:
            return cls.empty(from_commit_id, to_commit_id)

        updated_chunks = {chunk_id: len(chunk_indices) for chunk_id, chunk_indices in diff.updated_chunks.items()}

        return cls(
            from_commit_id=CommitId(from_commit_id) if from_commit_id else None,
            to_commit_id=CommitId(to_commit_id),
            new_groups=list(diff.new_groups),
            new_arrays=list(diff.new_arrays),
            deleted_groups=list(diff.deleted_groups),
            deleted_arrays=list(diff.deleted_arrays),
            updated_groups=list(diff.updated_groups),
            updated_arrays=list(diff.updated_arrays),
            updated_chunks=updated_chunks,
        )

    @classmethod
    def empty(cls, from_commit_id: str | None, to_commit_id: str) -> "CommitDiff":
        return cls(
            from_commit_id=CommitId(from_commit_id) if from_commit_id else None,
            to_commit_id=CommitId(to_commit_id),
            new_groups=[],
            new_arrays=[],
            deleted_groups=[],
            deleted_arrays=[],
            updated_groups=[],
            updated_arrays=[],
            updated_chunks={},
        )


class Branch(BaseModel):
    id: BranchName = Field(alias="_id")
    commit_id: CommitId
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class Tag(BaseModel):
    id: TagName
    commit_id: CommitId


class Tree(BaseModel):
    path: str
    metadata: Metadata
    children: dict[str, "Tree"]
    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    async def from_node(cls, node: AsyncGroup | AsyncArray, prefix: str = "", depth: int = 10) -> "Tree":
        if depth == 0 or not isinstance(node, AsyncGroup):
            return Tree(path=node.path, metadata=node.metadata, children={})

        children = {}
        async for name, member in node.members():
            if len(prefix) > 0 and not (prefix.startswith(member.path) or member.path.startswith(prefix)):
                continue
            children[name] = await Tree.from_node(member, prefix=prefix, depth=depth - 1)

        return Tree(path=node.path, metadata=node.metadata, children=children)

    @field_serializer("metadata")
    def metadata_field_serializer(self, v: Metadata):
        return json.loads(json.dumps(v.to_dict(), cls=V3JsonEncoder))


class GCResult(BaseModel):
    bytes_deleted: int
    chunks_deleted: int
    manifests_deleted: int
    snapshots_deleted: int
    attributes_deleted: int
    transaction_logs_deleted: int
    job_run_id: str | None = None


class ExpirationResult(BaseModel):
    released_snapshots: set[str]
    edited_snapshots: set[str]
    deleted_tags: set[str]
    deleted_branches: set[str]
    job_run_id: str | None = None
