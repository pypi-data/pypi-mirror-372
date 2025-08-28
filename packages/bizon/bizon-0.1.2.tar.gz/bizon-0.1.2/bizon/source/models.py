from datetime import datetime
from typing import List, Optional, Union

import polars as pl
from pydantic import BaseModel, Field, field_validator
from pytz import UTC

# Define the SourceRecord model
source_record_schema = pl.Schema(
    [
        ("id", str),
        ("data", str),  # JSON payload dumped as string
        ("timestamp", pl.Datetime(time_unit="us", time_zone="UTC")),
        ("destination_id", str),
    ]
)


### /!\ These models Source* will be used in all sources so we better never have to change them !!!
class SourceRecord(BaseModel):

    id: str = Field(..., description="Unique identifier of the record in the source")

    data: dict = Field(..., description="JSON payload of the record")

    timestamp: datetime = Field(
        default=datetime.now(tz=UTC),
        description="Timestamp of the record as defined by the source. Default is the time of extraction",
    )

    destination_id: Optional[str] = Field(None, description="Destination id")

    @field_validator("id", mode="before")
    def coerce_int_to_str(value: Union[int, str]) -> str:
        # Coerce int to str in case Source return id as int
        if isinstance(value, int):
            return str(value)
        return value


class SourceIteration(BaseModel):
    next_pagination: dict = Field(..., description="Next pagination to be used in the next iteration")
    records: List[SourceRecord] = Field(..., description="List of records retrieved in the current iteration")


class SourceIncrementalState(BaseModel):
    last_run: datetime = Field(..., description="Timestamp of the last successful run")
    state: dict = Field(..., description="Incremental state information from the latest sync")
