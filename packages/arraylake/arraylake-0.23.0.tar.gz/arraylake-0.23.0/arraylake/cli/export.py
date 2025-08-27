# mypy fails for zarr-v3
# mypy: ignore-errors

"""
DEPRECATED: This V1 export CLI module is pending removal.
V1 repositories are legacy and will be phased out in favor of Icechunk repositories.
This module and all its contents are scheduled for removal in a future version.
"""

import asyncio
import hashlib
import queue
import re
import threading
import time
import warnings
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from functools import partial
from os import rename
from os.path import isfile, splitext

import humanize
import s3fs
import tenacity
import yaml
import zarr
from packaging.version import Version
from rich.table import Table
from sqlitedict import SqliteDict

from arraylake.cli.utils import rich_console, simple_progress
from arraylake.client import AsyncClient, Client
from arraylake.repos.v1 import zarr_util
from arraylake.repos.v1.repo import AsyncRepo, Repo
from arraylake.repos.v1.types import CollectionName
from arraylake.types import DBIDBytes


@dataclass
class TransferStats:
    repo_name: str
    statefile_name: str
    n_docs: int = 0
    n_bytes: int = 0
    n_seconds: float = 0.0

    @property
    def bytes_human(self):
        return humanize.naturalsize(self.n_bytes)

    @property
    def seconds_human(self):
        return humanize.precisedelta(timedelta(seconds=self.n_seconds))

    @property
    def transfer_rate(self):
        if self.n_seconds > 0:
            transfer = self.n_bytes / self.n_seconds
        else:
            transfer = 0.0
        return f"{humanize.naturalsize(transfer)}/s"

    def to_table(self):
        table = Table(title=f"Export summary for [bold]{self.repo_name}[/bold]", min_width=80)
        table.add_column("Stat", justify="left", style="cyan", no_wrap=True, min_width=45)
        table.add_column("Value", justify="right", style="green", min_width=25)

        stats_and_headers = {
            "Objects transferred": self.n_docs,
            "Data transferred": self.bytes_human,
            "Export time": self.seconds_human,
            "Transfer rate": self.transfer_rate,
        }

        for name, val in stats_and_headers.items():
            table.add_row(name, str(val))

        return table


# CHUNK_PATH_PATTERN = r"c(\/\d+)*\d+$"
METADATA_PATH_PATTERN = r".json$"


class SupportedExportFormats(str, Enum):
    zarr2 = "zarr2"
    zarr3alpha = "zarr3alpha"


class ExportTarget:
    # FIXME: More sanity checks on the target
    def __init__(self, destination, format, extra_config):
        self.destination = destination
        self.format = format
        self.extra_config = extra_config
        self.transform_path = self._get_path_transformer()

    async def setup(self, loop=None):
        zarr_version = None
        if self.format == SupportedExportFormats.zarr2:
            zarr_version = 2
        elif self.format in {
            SupportedExportFormats.zarr3alpha,
        }:
            # FIXME: We need to do some library checks to see which v3 the
            # customer is intending to target...
            zarr_version = 3
        else:
            raise NotImplementedError

        if self.extra_config is None:
            extra_config_data = {}
        elif isinstance(self.extra_config, dict):
            extra_config_data = self.extra_config
        else:
            with open(self.extra_config) as f:
                extra_config_data = yaml.safe_load(f)

        # if using S3, we need to set up special options
        if str(self.destination).startswith("s3://"):
            fs = s3fs.S3FileSystem(
                anon=False,
                endpoint_url=extra_config_data.get("endpoint_url"),
                key=extra_config_data.get("access_key_id"),
                secret=extra_config_data.get("secret_access_key"),
            )
            store = fs.get_mapper(root=self.destination, check=False)
        else:
            store = self.destination

        self.group = zarr.open_group(store=store, mode="a", zarr_version=zarr_version)

    def _get_path_transformer(self):
        match self.format:
            case SupportedExportFormats.zarr2:
                # convert from data/root/foo/bar/c0/1/2 -> /foo/bar/0.1.2
                path_offset = len(zarr_util.DATA_ROOT)
                assert path_offset == len(zarr_util.META_ROOT)

                def _rewrite(source_path):
                    # chop off the "data/root/" or "meta/root/" prefixes
                    logical_path = source_path[path_offset:]

                    # if this is a chunk path, translate from slash- to
                    # dot-delimited
                    v3_pattern = r"c\d+(\/\d+)*$"
                    match = re.search(v3_pattern, logical_path)
                    if match:
                        i = match.start()
                        array_prefix = logical_path[:i]
                        chunk_path = logical_path[i:][1:].replace("/", ".")
                        return f"{array_prefix}{chunk_path}"
                    else:
                        return logical_path

                return _rewrite
            case SupportedExportFormats.zarr3alpha:
                return lambda path: path
            case _:
                raise NotImplementedError

    def delete(self, source_path) -> None:
        dest_path = self.transform_path(source_path)
        del self.group.store[dest_path]
        assert dest_path not in self.group.store

    def write(self, source_path, bytes) -> int:
        dest_path = self.transform_path(source_path)
        self.group.store[dest_path] = bytes
        return len(bytes)


class ExportManager:
    def __init__(
        self,
        repo: str | Repo,
        target: ExportTarget,
        *,
        ref: None | str = None,
        from_ref: None | str = None,
        concurrency: int = 64,
        validate: bool = False,
    ):
        if Version(zarr.__version__) > Version("3.0.0.a0"):
            raise ImportError("Exporting Icechunk repos is not supported at this time!")
        if isinstance(repo, str):
            self.repo_name = repo
            self.repo = None
        elif isinstance(repo, Repo):
            self.repo = repo
            self.repo_name = repo._arepo.repo_name
        self.from_ref = from_ref
        self.ref = ref

        self.from_commit: DBIDBytes | None = None
        self.as_of_commit: DBIDBytes | None = None

        self.target = target
        self.concurrency = concurrency
        self.validate = validate

        self.stats = TransferStats(self.repo_name, statefile_name="")

    async def __aenter__(self):
        # Check out repos
        with simple_progress(f"Checking out [bold]{self.repo_name}[/bold]..."):
            await self._checkout()

        # Set up statefile and init destination
        await self.target.setup(loop=asyncio.get_running_loop())
        self.statefile = await self._init_statefile()

        # contains a list of paths to be transferred
        # TODO: put the contents of the statefile as well
        self.download_queue: queue.Queue = queue.Queue()
        # contains a tuple of (path, bytes) to be written
        self.upload_queue: queue.Queue = queue.Queue(maxsize=self.concurrency)
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        # FIXME: If completed successfully, delete the statefile?
        if self.statefile:
            self.statefile.close()

        # Regardless of whether the transfer was a success or not, print a
        # summary report with the relevant metadata and stats.
        self.report()

    async def _checkout(self):
        repo = Client().get_repo(self.repo_name, checkout=False)

        # TODO: change to check for a v1 repo
        if not isinstance(repo, Repo):
            raise ValueError(f"Unexpected repo type: {type(repo)}")

        self.repo = repo

        if self.ref:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="You are not on a branch tip", category=UserWarning)
                self.repo.checkout(self.ref, for_writing=True)
        else:
            self.repo.checkout(for_writing=True)

        client = AsyncClient()
        async_repo = await client.get_repo(self.repo_name, checkout=False)

        if not isinstance(async_repo, AsyncRepo):
            raise ValueError(f"Unexpected async repo type: {type(async_repo)}")

        self.async_repo = async_repo

        self.as_of_commit = self.repo.session.base_commit
        assert self.as_of_commit
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="You are not on a branch tip", category=UserWarning)
            await self.async_repo.checkout(self.as_of_commit, for_writing=True)

        if self.from_ref:
            self.from_commit, _ = await self.async_repo._get_ref_for_checkout(self.from_ref)

    async def _changes_since(self, commit_id):
        metadata_collection = CollectionName("metadata")
        chunks_collection = CollectionName("chunks")
        nodes_collection = CollectionName("nodes")

        # Iterate over all commits, in chronological order, fetching
        # the deltas across all collections.
        assert self.repo is not None
        log = self.repo.commit_log
        changes = {}
        commits = []
        for commit in log:
            if commit.id == commit_id:
                break
            else:
                commits.append(commit)

        for commit in reversed(commits):
            for collection in (
                metadata_collection,
                chunks_collection,
                nodes_collection,
            ):
                # FIXME: These are synchronous and serialized, which kills
                # performance. I'd really prefer that all of this happened
                # asynchronously. Not a high priority in the grand scheme of
                # things, but this should be rewritten to use arepo and act
                # as an async generator.
                for change in self.repo._wrap_async_iter(
                    self.repo._arepo.db.get_all_paths_for_commit,
                    commit_id=commit.id,
                    collection=collection,
                ):
                    is_chunk_path = change.path.startswith(zarr_util.DATA_ROOT)

                    # Ignore path prefixes
                    if is_chunk_path:
                        changes[change.path] = {"d": change.deleted, "t": 0, "c": False}
                    else:
                        dest = None
                        prefix_offset = len(zarr_util.META_ROOT)
                        modified_entity = splitext(splitext(change.path[prefix_offset:])[0])[0]
                        if change.path.endswith(".array.json"):
                            src = self.repo.root_group[modified_entity]
                            dest = self.target.group.require_dataset(modified_entity, **self._args_from_array(src), overwrite=False)
                        elif change.path.endswith(".group.json"):
                            dest = self.target.group.require_group(modified_entity, overwrite=False)
                        else:
                            raise KeyError(f"Not a valid metadata path: {change.path}")
                        dest.attrs.update(**self.repo.root_group[modified_entity].attrs.asdict())

        return changes

    def _args_from_array(self, arr):
        return {
            "shape": arr.shape,
            "chunks": arr.chunks,
            "dtype": arr.dtype,
            "compressor": arr.compressor,
            "order": arr.order,
            "filters": arr.filters,
            "fill_value": arr.fill_value,
        }

    # NOTE: This process is currently not checkpointed, so it does not
    # support resumption. It is also dog slow.
    def _copy_metadata(self, statefile, path, item):
        from zarr.core import Array

        assert self.repo is not None
        src = self.repo.root_group[path]
        dest = None

        if isinstance(src, Array):
            dest = self.target.group.create_dataset(path, **self._args_from_array(src), overwrite=True)
            # Load all the chunk paths for the array into the statefile.
            # FIXME: This could be rewritten to take advantage of arepo and
            # consume the async generator _list_prefix.
            for chunk_path in self.repo.root_group.store.list_prefix(f"{zarr_util.DATA_ROOT}{path}"):
                # FIXME: add to statefile only if it doesn't already exist
                statefile[chunk_path] = {
                    "d": False,  # path to be deleted?
                    "t": 0,  # n_bytes transferred
                    "c": False,  # checksum validated?
                }

            statefile.commit()
        else:
            dest = self.target.group.require_group(path, overwrite=False)
        dest.attrs.update(**src.attrs.asdict())

    def _mk_statefile_name(self):
        # FIXME: Don't shove so much metadata into the filename. Use a proper
        # metadata table for all this info.
        repo = self.repo_name.replace("/", ".")
        from_commit = f"{self.from_commit}-" if self.from_commit else ""
        assert self.repo is not None
        to_commit = self.repo.session.base_commit
        target_hash = hashlib.sha256(str(self.target.destination).encode()).hexdigest()[:10]

        return f"{repo}.{from_commit}{to_commit}.{target_hash}.state"

    async def _init_statefile(self):
        assert self.repo is not None
        self.statefile_name = self._mk_statefile_name()
        self.stats.statefile_name = self.statefile_name
        if not isfile(self.statefile_name):
            # We don't have an existing statefile, which means we need to set
            # one up and initialize the destination store.
            temp_statefile_name = f"{self.statefile_name}.incomplete"
            temp_statefile = SqliteDict(temp_statefile_name)

            if self.from_commit:
                # The user wants an incremental update.
                with simple_progress(
                    f"Generating manifest from changes between [bold]{self.from_commit}[/bold] and [bold]{self.as_of_commit}[/bold]..."
                ):
                    changes = await self._changes_since(self.from_commit)

                    # Add data and metadata changes, including deletes.
                    for path, body in changes.items():
                        temp_statefile[path] = body
                    temp_statefile.commit()
            else:
                # This is a new export.
                with simple_progress(f"Generating manifest for full export as of [bold]{self.as_of_commit}[/bold]..."):
                    # FIXME: This is reeeeeeeeeeally slow.
                    self.repo.root_group.visititems(partial(self._copy_metadata, temp_statefile))
                    # don't forget the root group metadata
                    self._copy_metadata(temp_statefile, "", self.repo.root_group)

            # Once all changes have been committed, close the file and
            # move it to its proper location. This functions as a rough
            # transactional mechanism, so that we know any statefile without
            # the ".incomplete" suffix is complete. This prevents partial
            # exports.
            temp_statefile.close()
            rename(temp_statefile_name, self.statefile_name)

        return SqliteDict(self.statefile_name)

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_random_exponential(multiplier=1, max=60),
    )
    def _download_item(self):
        assert self.repo is not None
        path, change = self.download_queue.get()
        assert change["t"] == 0
        if change["d"]:
            # FIXME: validate this works for metadata updates
            self.target.delete(path)

            # we set "t" to -1 to indicate that the path has been
            # successfully deleted
            self.statefile[path] = {"d": True, "t": -1, "c": False}
        else:
            if zarr_util.is_chunk_key(path):
                # repo has no validate kwarg
                raw_data = self.repo._get_chunk(path)  # , validate=self.validate)
            else:
                raise KeyError(f"Not a valid chunk path: {path}")
            # add to upload queue (potentially block if queue is full)
            self.upload_queue.put((path, raw_data))

        self.download_queue.task_done()

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_random_exponential(multiplier=1, max=60),
    )
    def _upload_item(self):
        path, raw_data = self.upload_queue.get()
        n_bytes = self.target.write(path, raw_data)
        n_docs = 1
        self.statefile[path] = {
            "d": False,
            "t": n_bytes,
            "c": self.validate,
        }
        self.statefile.commit()
        self.upload_queue.task_done()
        self.stats.n_docs += n_docs
        self.stats.n_bytes += n_bytes
        self.pbar.update(self.task_id, advance=n_docs)

    async def copy_data(self):
        start_time = time.time()

        if self.statefile:
            n_items = len(self.statefile)

            with simple_progress(
                f"Exporting files to [bold]{self.target.destination}[/bold]... ",
                total=n_items,
            ) as progress:
                assert progress
                self.pbar = progress[0]
                self.task_id = progress[1]

                # Although slightly slower, using a deterministic sorting for the keys
                # ensures a more pleasant user experience, as the progress bar resumes
                # from where it left off.
                for path, change in sorted(self.statefile.items()):
                    if change["t"] == 0:
                        self.download_queue.put_nowait((path, change))
                    else:
                        self.pbar.update(self.task_id, advance=1)

                def download_worker_function():
                    while True:
                        self._download_item()

                def upload_worker_function():
                    while True:
                        self._upload_item()

                nworkers = self.concurrency // 2
                for _ in range(nworkers):
                    threading.Thread(target=download_worker_function, daemon=True).start()
                    threading.Thread(target=upload_worker_function, daemon=True).start()

                self.download_queue.join()
                self.upload_queue.join()
        else:
            rich_console.print("No documents to transfer!")
        self.stats.n_seconds = time.time() - start_time

    def report(self):
        # Print a nicely-formatted table
        rich_console.print(self.stats.to_table())
