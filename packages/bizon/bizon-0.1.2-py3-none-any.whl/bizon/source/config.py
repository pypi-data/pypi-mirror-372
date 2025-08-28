from abc import ABC
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from .auth.config import AuthConfig


class SourceSyncModes(str, Enum):

    # Full refresh
    # - creates a new StreamJob
    # - start syncing data from scratch till pagination is empty
    FULL_REFRESH = "full_refresh"

    # Incremental syncs data
    # - get the last successful sync start_date from previous succeeded StreamJob
    # - create a new StreamJob
    # - sync data till pagination is empty
    INCREMENTAL = "incremental"

    # Stream mode
    # - get single RUNNING streamJob syncs data from the last successfuly committed offset in the source system
    STREAM = "stream"


class APIConfig(BaseModel):
    retry_limit: Optional[int] = Field(100, description="Number of retries before giving up", example=100)


class SourceConfig(BaseModel, ABC):

    # Connector identifier to use, match a unique connector code
    name: str = Field(..., description="Name of the source to sync")
    stream: str = Field(..., description="Name of the stream to sync")

    source_file_path: Optional[str] = Field(
        default=None, description="Path to the source file, if not provided will look into bizon internal sources"
    )

    sync_mode: SourceSyncModes = Field(
        description="Sync mode to use",
        default=SourceSyncModes.FULL_REFRESH,
    )

    force_ignore_checkpoint: bool = Field(
        description="Whether to force recreate the sync from iteration 0. Existing checkpoints will be ignored.",
        default=False,
    )

    authentication: Optional[AuthConfig] = Field(
        description="Configuration for the authentication",
        default=None,
    )

    max_iterations: Optional[int] = Field(
        description="Maximum number of iterations for pulling from source, if None, run till all records are synced from source",  # noqa
        default=None,
    )

    api_config: APIConfig = Field(
        description="Configuration for the API client",
        default=APIConfig(retry_limit=10),
    )

    init_pipeline: bool = Field(
        description="[Used for testing] Whether to initialize the source to run pipeline directly.",
        default=True,
    )
