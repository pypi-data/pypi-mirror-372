# ----------------------------------------------------------------------
# Gufo Liftbridge: Data Types
# ----------------------------------------------------------------------
# Copyright (C) 2022-25, Gufo Labs
# See LICENSE.md for details
# ----------------------------------------------------------------------
"""Types definitions."""

# Python modules
from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List

# Gufo Liftbridge modules
from .api_pb2 import (
    AckPolicy as _AckPolicy,
)
from .api_pb2 import (
    StartPosition as _StartPosition,
)


class AckPolicy(IntEnum):
    """
     Publish acknowledgment policy.

    Attributes:
        LEADER: Wait for acknowledgment from a leader.
        ALL: Wait for acknowledgment from all cluster members.
        NONE: Do not wait for an acknowledgment.
    """

    LEADER = _AckPolicy.LEADER
    ALL = _AckPolicy.ALL
    NONE = _AckPolicy.NONE


class StartPosition(IntEnum):
    """
    Subscriber's start position.

    Attributes:
        NEW_ONLY: Start from new messages beyond the latest published.
        OFFSET: Start at a specified offset.
        EARLIEST: Start at the oldest message remaining in a partition.
        LATEST: Start with the newest message.
        TIMESTAMP: Start from a specified timestamp.
        RESUME: Non-standard. Resume from next to last processed.
    """

    NEW_ONLY = _StartPosition.NEW_ONLY
    OFFSET = _StartPosition.OFFSET
    EARLIEST = _StartPosition.EARLIEST
    LATEST = _StartPosition.LATEST
    TIMESTAMP = _StartPosition.TIMESTAMP
    RESUME = 9999


@dataclass(frozen=True)
class RetentionPolicy(object):
    """
    Partition's retention policy.

    Attributes:
        retention_bytes: Keep up to `retention_bytes` in a partition.
        segment_bytes:
        retention_ages:
        segment_ages:
    """

    retention_bytes: int = 0
    segment_bytes: int = 0
    retention_ages: int = 86400
    segment_ages: int = 3600


@dataclass
class Broker(object):
    """
    Broker node metadata.

    Attributes:
        id: Broker id.
        host: Broker host.
        port: Broker port.
    """

    id: str
    host: str
    port: int


@dataclass
class PartitionMetadata(object):
    """
    Partition metadata.

    Attributes:
        id: Partition id.
        leader: Leader broker id.
        replicas: Replica nodes.
        isr:
        high_watermark: Highest uncommited offset in partition.
        newest_offset: Offset for the next record.
        paused: Partition is paused.
    """

    id: int
    leader: str
    replicas: List[str]
    isr: List[str]
    high_watermark: int
    newest_offset: int
    paused: bool


@dataclass
class StreamMetadata(object):
    """
    Stream metadata.

    Attributes:
        name: Stream name.
        subject: Stream subject.
        partitions: List of partitions metadata.
    """

    name: str
    subject: str
    partitions: Dict[int, PartitionMetadata]


@dataclass
class Metadata(object):
    """
    Liftbridge cluster metadata.

    Attributes:
        brockers: List of brokers.
        metadata: List of stream's metadata.
    """

    brokers: List[Broker]
    metadata: List[StreamMetadata]


@dataclass
class Message(object):
    """
    Liftbridge message.

    Args:
        value: Message body.
        subject: Message stream.
        offset: Message offset.
        timestamp: Message timestamp in UNIX format.
        key: Message key.
        partition: stream partition.
        headers: Additional message headers.
    """

    value: bytes
    subject: str
    offset: int
    timestamp: int
    key: bytes
    partition: int
    headers: Dict[str, bytes]
