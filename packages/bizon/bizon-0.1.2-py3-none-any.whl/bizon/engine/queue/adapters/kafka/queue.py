import json
from typing import Union

from kafka import KafkaProducer
from loguru import logger

from bizon.destination.destination import AbstractDestination
from bizon.engine.queue.config import QUEUE_TERMINATION, QueueMessage
from bizon.engine.queue.queue import AbstractQueue

from .config import KafkaConfigDetails
from .consumer import KafkaConsumer_


class KafkaQueue(AbstractQueue):

    def __init__(self, config: KafkaConfigDetails) -> None:
        super().__init__(config)
        self.config: KafkaConfigDetails = config

    def connect(self):
        self.producer = self.get_kafka_producer()

    def get_consumer(self, destination: AbstractDestination) -> KafkaConsumer_:
        return KafkaConsumer_(config=self.config, destination=destination)

    def get_kafka_producer(self) -> KafkaProducer:
        return KafkaProducer(
            bootstrap_servers=self.config.queue.bootstrap_server,
            value_serializer=lambda m: json.dumps(m).encode("utf-8"),
        )

    @staticmethod
    def on_success(metadata):
        logger.info(f"Message produced to topic '{metadata.topic}' at offset {metadata.offset}")

    @staticmethod
    def on_error(e):
        logger.error(f"Error sending message: {e}")

    def get_size(self) -> Union[int, None]:
        return None

    def put_queue_message(self, queue_message: QueueMessage):
        future = self.producer.send(
            topic=self.config.queue.topic,
            value=queue_message.model_dump(),
        )
        future.add_callback(self.on_success)
        future.add_errback(self.on_error)
        self.producer.flush()

    def get(self) -> QueueMessage:
        raise NotImplementedError("Kafka does not support getting messages from here. Use KafkaConsumer instead.")

    def terminate(self, iteration: int) -> bool:
        self.put(source_records=[], iteration=iteration, signal=QUEUE_TERMINATION)
        self.producer.close()
        logger.debug("Terminating Kafka producer ...")
        return True
