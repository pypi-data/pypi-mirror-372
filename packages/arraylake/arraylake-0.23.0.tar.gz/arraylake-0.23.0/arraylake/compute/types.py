from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ServiceType(str, Enum):
    dap = "dap2"
    edr = "edr"
    wms = "wms"
    tiles = "tiles"
    zarr = "zarr"


class ServiceStatus(str, Enum):
    available = "available"
    progressing = "progressing"
    unknown = "unknown"
    error = "error"


class LogLevel(str, Enum):
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"
    critical = "CRITICAL"


class ServiceConfig(BaseModel):
    service_type: ServiceType
    org: str

    # NOTE: This is necessary to have our unauthenticated, public-facing demos.
    #
    # NOTE: An org can only have one public or private instance of a given
    # service deployed at a time, as the routing is ambiguous if we were to
    # support multiple different instances.
    is_public: bool

    # Optional Booth image tag
    service_version: Optional[str] = None

    # Optional scaling parameters
    min_replicas: Optional[int] = 1
    max_replicas: Optional[int] = 10

    # Optional Booth store cache duration (in seconds)
    store_cache_ttl: Optional[int] = 60

    # Optional Booth store cache max number of datasets
    store_cache_size: Optional[int] = 10

    # Optional cache max-age for cache control headers of the service responses (in seconds)
    # If not set, the default is 0, which means functionally no caching, but requests are revalidated.
    cache_max_age: Optional[int] = 0

    # Optional control over icechunk chunk cache size in bytes
    icechunk_cache_chunk_bytes: Optional[int] = 1024 * 1024 * 1024

    # Optional control over the number of chunk refs icechunk cache
    icechunk_cache_chunk_ref_count: Optional[int] = 10_000_000

    # Optional zarr concurrency configuration, the number of concurrent reads zarr will use fulfilling requests
    zarr_concurrency: Optional[int] = 25

    # Optional log level for the service
    log_level: Optional[LogLevel] = LogLevel.info

    def __str__(self) -> str:
        return f"{self.service_type.value}://{self.org}"


class DeploymentInfo(BaseModel):
    """Compute deployment information."""

    name: str
    url: str
    created: datetime
    config: ServiceConfig
    status: ServiceStatus


class LoadResults(BaseModel):
    succeeded: list[str]
    failed: list[str]


class ComputeConfig(BaseModel):
    service_uri: str
    domain: str
    env: str
    container_repository: str
    kube_config: dict
    openmeter_api_key: Optional[str] = None


class LogMessage(BaseModel):
    time: str
    message: str

    def __str__(self) -> str:
        return f"{self.time} | {self.message}\n"

    @classmethod
    def from_log_line(cls, log: str) -> "LogMessage":
        """Parse a log line into a LogMessage object.

        Example log line:
        # "2025-03-29T19:30:15.505397124Z stderr F INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)"

        The log line is split into a timestamp, stream, completeness, and message. For now we ignore the stream
        and completeness.
        """
        time, _stream, _completeness, *message = log.split(" ")
        return cls(time=time, message=" ".join(message))
