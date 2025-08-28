from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from bizon.alerting.models import AlertingConfig
from bizon.connectors.destinations.bigquery.src.config import BigQueryConfig
from bizon.connectors.destinations.bigquery_streaming.src.config import (
    BigQueryStreamingConfig,
)
from bizon.connectors.destinations.bigquery_streaming_v2.src.config import (
    BigQueryStreamingV2Config,
)
from bizon.connectors.destinations.file.src.config import FileDestinationConfig
from bizon.connectors.destinations.logger.src.config import LoggerConfig
from bizon.engine.config import EngineConfig
from bizon.monitoring.config import MonitoringConfig
from bizon.source.config import SourceConfig, SourceSyncModes
from bizon.transform.config import TransformModel


class BizonConfig(BaseModel):

    # Forbid extra keys in the model
    model_config = ConfigDict(extra="forbid")

    # Unique name to identify the sync configuration
    name: str = Field(..., description="Unique name for this sync configuration")

    source: SourceConfig = Field(
        description="Source configuration",
        default=...,
    )

    transforms: Optional[list[TransformModel]] = Field(
        description="List of transformations to apply to the source data",
        default=[],
    )

    destination: Union[
        BigQueryConfig,
        BigQueryStreamingConfig,
        BigQueryStreamingV2Config,
        LoggerConfig,
        FileDestinationConfig,
    ] = Field(
        description="Destination configuration",
        discriminator="name",
        default=...,
    )

    engine: EngineConfig = Field(
        description="Engine configuration",
        default=EngineConfig(),
    )

    alerting: Optional[AlertingConfig] = Field(
        description="Alerting configuration",
        default=None,
    )

    monitoring: Optional[MonitoringConfig] = Field(
        description="Monitoring configuration",
        default=None,
    )


class SyncMetadata(BaseModel):
    """Model which stores general metadata around a sync.
    Facilitate usage of basic info across entities
    """

    name: str
    job_id: str
    source_name: str
    stream_name: str
    sync_mode: SourceSyncModes
    destination_name: str
    destination_alias: str

    @classmethod
    def from_bizon_config(cls, job_id: str, config: BizonConfig) -> "SyncMetadata":
        return cls(
            name=config.name,
            job_id=job_id,
            source_name=config.source.name,
            stream_name=config.source.stream,
            sync_mode=config.source.sync_mode,
            destination_name=config.destination.name,
            destination_alias=config.destination.alias,
        )
