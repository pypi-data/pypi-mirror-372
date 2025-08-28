from typing import Literal

from pydantic import BaseModel, Field

from bizon.engine.queue.config import (
    AbastractQueueConfigDetails,
    AbstractQueueConfig,
    QueueTypes,
)


class PythonQueueQueueConfig(BaseModel):
    max_size: int = Field(0, description="Maximum size of the queue, by default 0 means unlimited")


class PythonQueueConsumerConfig(BaseModel):
    poll_interval: int = Field(1, description="Interval in seconds to poll the queue in seconds")


class PythonQueueConfigDetails(AbastractQueueConfigDetails):
    queue: PythonQueueQueueConfig = Field(
        default=PythonQueueQueueConfig(max_size=0), description="Configuration of the queue"
    )
    consumer: PythonQueueConsumerConfig = Field(
        default=PythonQueueConsumerConfig(poll_interval=1), description="Kafka consumer configuration"
    )


class PythonQueueConfig(AbstractQueueConfig):
    type: Literal[QueueTypes.PYTHON_QUEUE]
    config: PythonQueueConfigDetails
