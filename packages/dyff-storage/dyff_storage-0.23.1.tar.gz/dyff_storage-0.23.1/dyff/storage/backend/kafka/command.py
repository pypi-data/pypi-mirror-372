# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
import json
from typing import TypeVar

import pydantic
from confluent_kafka import Producer

from dyff.schema.commands import DyffCommandType
from dyff.schema.platform import DyffEntity, DyffEntityType
from dyff.storage.config import config
from dyff.storage.typing import YAMLObject

from ..base.command import CommandBackend


def serialize_id(id: str) -> bytes:
    return id.encode("utf-8")


def serialize_value(value: YAMLObject) -> bytes:
    return json.dumps(value).encode("utf-8")


def serialize_entity(entity: DyffEntity) -> bytes:
    return entity.json().encode("utf-8")


def deserialize_id(id: bytes) -> str:
    return id.decode("utf-8")


def deserialize_value(value: bytes) -> YAMLObject:
    return json.loads(value.decode("utf-8"))


def deserialize_entity(entity: bytes) -> DyffEntityType:
    s = entity.decode("utf-8")
    # DyffEntityType is a pydantic "discriminated union", so pydantic infers
    # the type from the '.kind' field
    return pydantic.parse_raw_as(DyffEntityType, s)  # type: ignore


EntityT = TypeVar("EntityT", bound=DyffEntity)


class KafkaCommandBackend(CommandBackend):
    """Implementation of the Command model using Kafka streams."""

    def __init__(self):
        self.events_topic = config.kafka.topics.workflows_events
        producer_config = config.kafka.config.get_producer_config()
        # FIXME: This should be the global default. It's supposed to be the
        # default in Kafka > 3.0, but the docs of librdkafka suggest that
        # its default is still False.
        # See: https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md
        producer_config["enable.idempotence"] = True
        # FIXME: See comment in alignmentlabs.dyff.web.server
        # Can't get real logging to work when running in uvicorn
        print(
            f"Creating KafkaCommandBackend with config:\n{json.dumps(producer_config, indent=2)}",
            flush=True,
        )
        # logging.info(f"Creating KafkaCommandBackend with config:\n{json.dumps(producer_config, indent=2)}")
        self._kafka_producer = Producer(producer_config)

    def close(self) -> None:
        """Shut down the command backend cleanly."""
        if self._kafka_producer:
            self._kafka_producer.flush()
        self._kafka_producer = None

    def execute(self, command: DyffCommandType) -> None:
        message = command.model_dump(mode="json")
        self._kafka_producer.produce(
            topic=self.events_topic,
            value=serialize_value(message),
            # TODO: There may one day be commands that don't have a .data.id
            # property because they don't apply to a single entity.
            key=serialize_id(command.data.id),
        )
