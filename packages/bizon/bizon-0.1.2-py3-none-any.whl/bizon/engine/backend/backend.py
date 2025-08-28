from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.orm import Session

from .config import AbstractBackendConfig, AbstractBackendConfigDetails, BackendTypes
from .models import CursorStatus, DestinationCursor, JobStatus, SourceCursor, StreamJob


class AbstractBackend(ABC):
    def __init__(self, config: AbstractBackendConfigDetails, type: BackendTypes, **kwargs):
        self.type = type
        self.config = config

    @abstractmethod
    def create_all_tables(self):
        """Create all tables in the database"""
        pass

    @abstractmethod
    def drop_all_tables(self):
        """Drop all tables in the database"""
        pass

    @abstractmethod
    def check_prerequisites(self) -> bool:
        """Check if the database contains the necessary tables, return True if entities are present
        Return False if entities are not present, they will be created
        """
        pass

    @abstractmethod
    def create_stream_job(
        self,
        name: str,
        source_name: str,
        stream_name: str,
        sync_mode: str,
        total_records_to_fetch: Optional[int] = None,
        job_status: JobStatus = JobStatus.STARTED,
        session: Optional[Session] = None,
    ) -> StreamJob:
        """Create new StreamJob record in db and return it"""
        pass

    @abstractmethod
    def update_stream_job_status(
        self, job_id: str, job_status: JobStatus, error_message: Optional[str] = None, session: Optional[Session] = None
    ):
        """Update the status of the stream job with the given id"""
        pass

    @abstractmethod
    def get_stream_job_by_id(self, job_id: str, session: Optional[Session] = None) -> Optional[StreamJob]:
        """Get the job by its ID"""
        pass

    @abstractmethod
    def get_running_stream_job(
        self, name: str, source_name: str, stream_name: str, session: Optional[Session] = None
    ) -> Optional[StreamJob]:
        """Get the job id for the given source and stream name"""
        pass

    @abstractmethod
    def get_last_successful_stream_job(
        self, name: str, source_name: str, stream_name: str, session: Optional[Session] = None
    ) -> Optional[StreamJob]:
        """Get the last successful job for the given source and stream name"""
        pass

    @abstractmethod
    def create_source_cursor(
        self,
        job_id: str,
        name: str,
        source_name: str,
        stream_name: str,
        iteration: int,
        rows_fetched: int,
        next_pagination: dict,
        cursor_status: CursorStatus = CursorStatus.STARTED,
        error_message: Optional[str] = None,
        session: Optional[Session] = None,
    ) -> str:
        """Create a new SourceCursor record in db and return its ID"""
        pass

    @abstractmethod
    def update_source_cursor_status(
        self,
        cursor_id: str,
        cursor_status: CursorStatus,
        error_message: Optional[str] = None,
        session: Optional[Session] = None,
    ):
        pass

    @abstractmethod
    def get_source_cursor_by_id(self, cursor_id: str, session: Optional[Session] = None) -> Optional[SourceCursor]:
        """Get the cursor by its ID"""
        pass

    @abstractmethod
    def get_last_cursor_by_job_id(self, job_id: str, session: Optional[Session] = None) -> Optional[DestinationCursor]:
        """Get the last cursor we should start source from for the given job id"""
        pass

    @abstractmethod
    def get_last_source_cursor_by_stream_and_iteration(
        self, name: str, source_name: str, stream_name: str, iteration: int, session: Optional[Session] = None
    ) -> Optional[SourceCursor]:
        """Get the last cursor for the given stream and iteration"""
        pass

    @abstractmethod
    def create_destination_cursor(
        self,
        job_id: str,
        name: str,
        source_name: str,
        stream_name: str,
        destination_name: str,
        from_source_iteration: int,
        to_source_iteration: int,
        rows_written: int,
        success: bool,
        pagination: Optional[dict] = None,
        session: Optional[Session] = None,
    ) -> DestinationCursor:
        """Create a new DestinationCursor record in db and return it"""
        pass

    @abstractmethod
    def get_destination_cursor_by_id(
        self, cursor_id: str, session: Optional[Session] = None
    ) -> Optional[DestinationCursor]:
        """Get the destination cursor by its ID"""
        pass

    @abstractmethod
    def get_number_of_written_rows_for_job(self, job_id: str, session: Optional[Session] = None) -> Optional[int]:
        """Get the number of written rows for the given job"""
        pass


class BackendFactory:
    @staticmethod
    def get_backend(config: AbstractBackendConfig, **kwargs) -> AbstractBackend:
        """Create a backend instance from the given config"""
        if config.type == BackendTypes.POSTGRES:
            from .adapters.sqlalchemy.backend import SQLAlchemyBackend

            return SQLAlchemyBackend(config=config.config, type=config.type, **kwargs)

        elif config.type == BackendTypes.BIGQUERY:
            from .adapters.sqlalchemy.backend import SQLAlchemyBackend

            return SQLAlchemyBackend(config=config.config, type=config.type, **kwargs)

        elif config.type == BackendTypes.SQLITE:
            from .adapters.sqlalchemy.backend import SQLAlchemyBackend

            return SQLAlchemyBackend(config=config.config, type=config.type, **kwargs)

        # ONLY FOR UNIT TESTS
        elif config.type == BackendTypes.SQLITE_IN_MEMORY:
            from .adapters.sqlalchemy.backend import SQLAlchemyBackend

            return SQLAlchemyBackend(config=config.config, type=config.type, **kwargs)

        raise ValueError(f"Unsupported backend type: {config.type}")
