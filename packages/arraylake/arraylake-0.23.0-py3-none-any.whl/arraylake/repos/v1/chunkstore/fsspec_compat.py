from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, TypedDict, Union

if TYPE_CHECKING:
    import gcsfs
    import s3fs


class Platform(Enum):
    S3 = 1
    GS = 2


# an unparsed, unspecified set of configuration options that will be used
# to initialize the an object store
GenericObjectStoreKwargs = dict[str, Union[str, bool]]


# configuration options that can be passed through to create a Boto3 client
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html#boto3.session.Session.client
S3BotoClientKwargs = dict[str, Union[str, bool]]


# a class which handles the special-casing of the `anon` argument for S3
# https://github.com/fsspec/s3fs/blob/74f4d95a62d7339a1af12db4339f22c5f3d73670/s3fs/core.py#L171
class S3FSConstructorKwargs(TypedDict, total=False):
    anon: bool
    client_kwargs: S3BotoClientKwargs


def GenericObjectStoreKwargs_to_S3FSConstructorKwargs(d: GenericObjectStoreKwargs) -> S3FSConstructorKwargs:
    anon = bool(d.pop("anon", False))
    return S3FSConstructorKwargs(anon=anon, client_kwargs=S3BotoClientKwargs(d))


# gcsfs works different from s3fs; there is no `anon` argument nor client_kwargs
# https://github.com/fsspec/gcsfs/blob/main/gcsfs/core.py#L154
GCSFSConstructorKwargs = dict[str, Union[str, bool]]


FSSpecConstructorKwargs = Union[S3FSConstructorKwargs, GCSFSConstructorKwargs]


@dataclass(frozen=True)
class S3FSConfig:
    fs: "s3fs.S3FileSystem"
    constructor_kwargs: S3FSConstructorKwargs
    platform: ClassVar[Platform] = Platform.S3
    protocol: ClassVar[str] = "s3"


@dataclass(frozen=True)
class GCSFSConfig:
    fs: "gcsfs.GCSFSFileSystem"
    constructor_kwargs: GCSFSConstructorKwargs
    platform: ClassVar[Platform] = Platform.GS
    protocol: ClassVar[str] = "gs"


FSConfig = Union[S3FSConfig, GCSFSConfig]
