from typing import List
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import (
    ClassVar as _ClassVar,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class StartPosition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NEW_ONLY: _ClassVar[StartPosition]
    OFFSET: _ClassVar[StartPosition]
    EARLIEST: _ClassVar[StartPosition]
    LATEST: _ClassVar[StartPosition]
    TIMESTAMP: _ClassVar[StartPosition]

class StopPosition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STOP_ON_CANCEL: _ClassVar[StopPosition]
    STOP_OFFSET: _ClassVar[StopPosition]
    STOP_LATEST: _ClassVar[StopPosition]
    STOP_TIMESTAMP: _ClassVar[StopPosition]

class AckPolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LEADER: _ClassVar[AckPolicy]
    ALL: _ClassVar[AckPolicy]
    NONE: _ClassVar[AckPolicy]

class ActivityStreamOp(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CREATE_STREAM: _ClassVar[ActivityStreamOp]
    DELETE_STREAM: _ClassVar[ActivityStreamOp]
    PAUSE_STREAM: _ClassVar[ActivityStreamOp]
    RESUME_STREAM: _ClassVar[ActivityStreamOp]
    SET_STREAM_READONLY: _ClassVar[ActivityStreamOp]
    JOIN_CONSUMER_GROUP: _ClassVar[ActivityStreamOp]
    LEAVE_CONSUMER_GROUP: _ClassVar[ActivityStreamOp]

NEW_ONLY: StartPosition
OFFSET: StartPosition
EARLIEST: StartPosition
LATEST: StartPosition
TIMESTAMP: StartPosition
STOP_ON_CANCEL: StopPosition
STOP_OFFSET: StopPosition
STOP_LATEST: StopPosition
STOP_TIMESTAMP: StopPosition
LEADER: AckPolicy
ALL: AckPolicy
NONE: AckPolicy
CREATE_STREAM: ActivityStreamOp
DELETE_STREAM: ActivityStreamOp
PAUSE_STREAM: ActivityStreamOp
RESUME_STREAM: ActivityStreamOp
SET_STREAM_READONLY: ActivityStreamOp
JOIN_CONSUMER_GROUP: ActivityStreamOp
LEAVE_CONSUMER_GROUP: ActivityStreamOp

class NullableInt64(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class NullableInt32(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class NullableBool(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bool
    def __init__(self, value: bool = ...) -> None: ...

class CreateStreamRequest(_message.Message):
    __slots__ = (
        "subject",
        "name",
        "group",
        "replicationFactor",
        "partitions",
        "retentionMaxBytes",
        "retentionMaxMessages",
        "retentionMaxAge",
        "cleanerInterval",
        "segmentMaxBytes",
        "segmentMaxAge",
        "compactMaxGoroutines",
        "compactEnabled",
        "autoPauseTime",
        "autoPauseDisableIfSubscribers",
        "minIsr",
        "optimisticConcurrencyControl",
        "encryption",
    )
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    REPLICATIONFACTOR_FIELD_NUMBER: _ClassVar[int]
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    RETENTIONMAXBYTES_FIELD_NUMBER: _ClassVar[int]
    RETENTIONMAXMESSAGES_FIELD_NUMBER: _ClassVar[int]
    RETENTIONMAXAGE_FIELD_NUMBER: _ClassVar[int]
    CLEANERINTERVAL_FIELD_NUMBER: _ClassVar[int]
    SEGMENTMAXBYTES_FIELD_NUMBER: _ClassVar[int]
    SEGMENTMAXAGE_FIELD_NUMBER: _ClassVar[int]
    COMPACTMAXGOROUTINES_FIELD_NUMBER: _ClassVar[int]
    COMPACTENABLED_FIELD_NUMBER: _ClassVar[int]
    AUTOPAUSETIME_FIELD_NUMBER: _ClassVar[int]
    AUTOPAUSEDISABLEIFSUBSCRIBERS_FIELD_NUMBER: _ClassVar[int]
    MINISR_FIELD_NUMBER: _ClassVar[int]
    OPTIMISTICCONCURRENCYCONTROL_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTION_FIELD_NUMBER: _ClassVar[int]
    subject: str
    name: str
    group: str
    replicationFactor: int
    partitions: int
    retentionMaxBytes: NullableInt64
    retentionMaxMessages: NullableInt64
    retentionMaxAge: NullableInt64
    cleanerInterval: NullableInt64
    segmentMaxBytes: NullableInt64
    segmentMaxAge: NullableInt64
    compactMaxGoroutines: NullableInt32
    compactEnabled: NullableBool
    autoPauseTime: NullableInt64
    autoPauseDisableIfSubscribers: NullableBool
    minIsr: NullableInt32
    optimisticConcurrencyControl: NullableBool
    encryption: NullableBool
    def __init__(
        self,
        subject: _Optional[str] = ...,
        name: _Optional[str] = ...,
        group: _Optional[str] = ...,
        replicationFactor: _Optional[int] = ...,
        partitions: _Optional[int] = ...,
        retentionMaxBytes: _Optional[_Union[NullableInt64, _Mapping]] = ...,
        retentionMaxMessages: _Optional[_Union[NullableInt64, _Mapping]] = ...,
        retentionMaxAge: _Optional[_Union[NullableInt64, _Mapping]] = ...,
        cleanerInterval: _Optional[_Union[NullableInt64, _Mapping]] = ...,
        segmentMaxBytes: _Optional[_Union[NullableInt64, _Mapping]] = ...,
        segmentMaxAge: _Optional[_Union[NullableInt64, _Mapping]] = ...,
        compactMaxGoroutines: _Optional[_Union[NullableInt32, _Mapping]] = ...,
        compactEnabled: _Optional[_Union[NullableBool, _Mapping]] = ...,
        autoPauseTime: _Optional[_Union[NullableInt64, _Mapping]] = ...,
        autoPauseDisableIfSubscribers: _Optional[
            _Union[NullableBool, _Mapping]
        ] = ...,
        minIsr: _Optional[_Union[NullableInt32, _Mapping]] = ...,
        optimisticConcurrencyControl: _Optional[
            _Union[NullableBool, _Mapping]
        ] = ...,
        encryption: _Optional[_Union[NullableBool, _Mapping]] = ...,
    ) -> None: ...

class CreateStreamResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteStreamRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class DeleteStreamResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PauseStreamRequest(_message.Message):
    __slots__ = ("name", "partitions", "resumeAll")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    RESUMEALL_FIELD_NUMBER: _ClassVar[int]
    name: str
    partitions: _containers.RepeatedScalarFieldContainer[int]
    resumeAll: bool
    def __init__(
        self,
        name: _Optional[str] = ...,
        partitions: _Optional[_Iterable[int]] = ...,
        resumeAll: bool = ...,
    ) -> None: ...

class PauseStreamResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetStreamReadonlyRequest(_message.Message):
    __slots__ = ("name", "partitions", "readonly")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    READONLY_FIELD_NUMBER: _ClassVar[int]
    name: str
    partitions: _containers.RepeatedScalarFieldContainer[int]
    readonly: bool
    def __init__(
        self,
        name: _Optional[str] = ...,
        partitions: _Optional[_Iterable[int]] = ...,
        readonly: bool = ...,
    ) -> None: ...

class SetStreamReadonlyResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Consumer(_message.Message):
    __slots__ = ("groupId", "groupEpoch", "consumerId")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    GROUPEPOCH_FIELD_NUMBER: _ClassVar[int]
    CONSUMERID_FIELD_NUMBER: _ClassVar[int]
    groupId: str
    groupEpoch: int
    consumerId: str
    def __init__(
        self,
        groupId: _Optional[str] = ...,
        groupEpoch: _Optional[int] = ...,
        consumerId: _Optional[str] = ...,
    ) -> None: ...

class SubscribeRequest(_message.Message):
    __slots__ = (
        "stream",
        "partition",
        "startPosition",
        "startOffset",
        "startTimestamp",
        "readISRReplica",
        "resume",
        "stopPosition",
        "stopOffset",
        "stopTimestamp",
        "consumer",
    )
    STREAM_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    STARTPOSITION_FIELD_NUMBER: _ClassVar[int]
    STARTOFFSET_FIELD_NUMBER: _ClassVar[int]
    STARTTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    READISRREPLICA_FIELD_NUMBER: _ClassVar[int]
    RESUME_FIELD_NUMBER: _ClassVar[int]
    STOPPOSITION_FIELD_NUMBER: _ClassVar[int]
    STOPOFFSET_FIELD_NUMBER: _ClassVar[int]
    STOPTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CONSUMER_FIELD_NUMBER: _ClassVar[int]
    stream: str
    partition: int
    startPosition: StartPosition
    startOffset: int
    startTimestamp: int
    readISRReplica: bool
    resume: bool
    stopPosition: StopPosition
    stopOffset: int
    stopTimestamp: int
    consumer: Consumer
    def __init__(
        self,
        stream: _Optional[str] = ...,
        partition: _Optional[int] = ...,
        startPosition: _Optional[_Union[StartPosition, str]] = ...,
        startOffset: _Optional[int] = ...,
        startTimestamp: _Optional[int] = ...,
        readISRReplica: bool = ...,
        resume: bool = ...,
        stopPosition: _Optional[_Union[StopPosition, str]] = ...,
        stopOffset: _Optional[int] = ...,
        stopTimestamp: _Optional[int] = ...,
        consumer: _Optional[_Union[Consumer, _Mapping]] = ...,
    ) -> None: ...

class FetchMetadataRequest(_message.Message):
    __slots__ = ("streams", "groups")
    STREAMS_FIELD_NUMBER: _ClassVar[int]
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    streams: _containers.RepeatedScalarFieldContainer[str]
    groups: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        streams: _Optional[_Iterable[str]] = ...,
        groups: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class FetchMetadataResponse(_message.Message):
    __slots__ = ("brokers", "streamMetadata", "groupMetadata")
    BROKERS_FIELD_NUMBER: _ClassVar[int]
    STREAMMETADATA_FIELD_NUMBER: _ClassVar[int]
    GROUPMETADATA_FIELD_NUMBER: _ClassVar[int]
    brokers: _containers.RepeatedCompositeFieldContainer[Broker]
    streamMetadata: _containers.RepeatedCompositeFieldContainer[StreamMetadata]
    groupMetadata: _containers.RepeatedCompositeFieldContainer[
        ConsumerGroupMetadata
    ]
    def __init__(
        self,
        brokers: _Optional[_Iterable[_Union[Broker, _Mapping]]] = ...,
        streamMetadata: _Optional[
            _Iterable[_Union[StreamMetadata, _Mapping]]
        ] = ...,
        groupMetadata: _Optional[
            _Iterable[_Union[ConsumerGroupMetadata, _Mapping]]
        ] = ...,
    ) -> None: ...

class FetchPartitionMetadataRequest(_message.Message):
    __slots__ = ("stream", "partition")
    STREAM_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    stream: str
    partition: int
    def __init__(
        self, stream: _Optional[str] = ..., partition: _Optional[int] = ...
    ) -> None: ...

class FetchPartitionMetadataResponse(_message.Message):
    __slots__ = ("metadata",)
    METADATA_FIELD_NUMBER: _ClassVar[int]
    metadata: PartitionMetadata
    def __init__(
        self, metadata: _Optional[_Union[PartitionMetadata, _Mapping]] = ...
    ) -> None: ...

class PublishRequest(_message.Message):
    __slots__ = (
        "key",
        "value",
        "stream",
        "partition",
        "headers",
        "ackInbox",
        "correlationId",
        "ackPolicy",
        "expectedOffset",
    )
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[bytes] = ...
        ) -> None: ...

    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    ACKINBOX_FIELD_NUMBER: _ClassVar[int]
    CORRELATIONID_FIELD_NUMBER: _ClassVar[int]
    ACKPOLICY_FIELD_NUMBER: _ClassVar[int]
    EXPECTEDOFFSET_FIELD_NUMBER: _ClassVar[int]
    key: bytes
    value: bytes
    stream: str
    partition: int
    headers: _containers.ScalarMap[str, bytes]
    ackInbox: str
    correlationId: str
    ackPolicy: AckPolicy
    expectedOffset: int
    def __init__(
        self,
        key: _Optional[bytes] = ...,
        value: _Optional[bytes] = ...,
        stream: _Optional[str] = ...,
        partition: _Optional[int] = ...,
        headers: _Optional[_Mapping[str, bytes]] = ...,
        ackInbox: _Optional[str] = ...,
        correlationId: _Optional[str] = ...,
        ackPolicy: _Optional[_Union[AckPolicy, str]] = ...,
        expectedOffset: _Optional[int] = ...,
    ) -> None: ...

class PublishAsyncError(_message.Message):
    __slots__ = ("code", "message")
    class Code(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[PublishAsyncError.Code]
        BAD_REQUEST: _ClassVar[PublishAsyncError.Code]
        NOT_FOUND: _ClassVar[PublishAsyncError.Code]
        INTERNAL: _ClassVar[PublishAsyncError.Code]
        READONLY: _ClassVar[PublishAsyncError.Code]
        INCORRECT_OFFSET: _ClassVar[PublishAsyncError.Code]
        ENCRYPTION_FAILED: _ClassVar[PublishAsyncError.Code]
        PERMISSION_DENIED: _ClassVar[PublishAsyncError.Code]

    UNKNOWN: PublishAsyncError.Code
    BAD_REQUEST: PublishAsyncError.Code
    NOT_FOUND: PublishAsyncError.Code
    INTERNAL: PublishAsyncError.Code
    READONLY: PublishAsyncError.Code
    INCORRECT_OFFSET: PublishAsyncError.Code
    ENCRYPTION_FAILED: PublishAsyncError.Code
    PERMISSION_DENIED: PublishAsyncError.Code
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: PublishAsyncError.Code
    message: str
    def __init__(
        self,
        code: _Optional[_Union[PublishAsyncError.Code, str]] = ...,
        message: _Optional[str] = ...,
    ) -> None: ...

class PublishResponse(_message.Message):
    __slots__ = ("ack", "asyncError", "correlationId")
    ACK_FIELD_NUMBER: _ClassVar[int]
    ASYNCERROR_FIELD_NUMBER: _ClassVar[int]
    CORRELATIONID_FIELD_NUMBER: _ClassVar[int]
    ack: Ack
    asyncError: PublishAsyncError
    correlationId: str
    def __init__(
        self,
        ack: _Optional[_Union[Ack, _Mapping]] = ...,
        asyncError: _Optional[_Union[PublishAsyncError, _Mapping]] = ...,
        correlationId: _Optional[str] = ...,
    ) -> None: ...

class PublishToSubjectRequest(_message.Message):
    __slots__ = (
        "key",
        "value",
        "subject",
        "headers",
        "ackInbox",
        "correlationId",
        "ackPolicy",
    )
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[bytes] = ...
        ) -> None: ...

    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    ACKINBOX_FIELD_NUMBER: _ClassVar[int]
    CORRELATIONID_FIELD_NUMBER: _ClassVar[int]
    ACKPOLICY_FIELD_NUMBER: _ClassVar[int]
    key: bytes
    value: bytes
    subject: str
    headers: _containers.ScalarMap[str, bytes]
    ackInbox: str
    correlationId: str
    ackPolicy: AckPolicy
    def __init__(
        self,
        key: _Optional[bytes] = ...,
        value: _Optional[bytes] = ...,
        subject: _Optional[str] = ...,
        headers: _Optional[_Mapping[str, bytes]] = ...,
        ackInbox: _Optional[str] = ...,
        correlationId: _Optional[str] = ...,
        ackPolicy: _Optional[_Union[AckPolicy, str]] = ...,
    ) -> None: ...

class PublishToSubjectResponse(_message.Message):
    __slots__ = ("ack",)
    ACK_FIELD_NUMBER: _ClassVar[int]
    ack: Ack
    def __init__(
        self, ack: _Optional[_Union[Ack, _Mapping]] = ...
    ) -> None: ...

class SetCursorRequest(_message.Message):
    __slots__ = ("stream", "partition", "cursorId", "offset")
    STREAM_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    CURSORID_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    stream: str
    partition: int
    cursorId: str
    offset: int
    def __init__(
        self,
        stream: _Optional[str] = ...,
        partition: _Optional[int] = ...,
        cursorId: _Optional[str] = ...,
        offset: _Optional[int] = ...,
    ) -> None: ...

class SetCursorResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FetchCursorRequest(_message.Message):
    __slots__ = ("stream", "partition", "cursorId")
    STREAM_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    CURSORID_FIELD_NUMBER: _ClassVar[int]
    stream: str
    partition: int
    cursorId: str
    def __init__(
        self,
        stream: _Optional[str] = ...,
        partition: _Optional[int] = ...,
        cursorId: _Optional[str] = ...,
    ) -> None: ...

class FetchCursorResponse(_message.Message):
    __slots__ = ("offset",)
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    offset: int
    def __init__(self, offset: _Optional[int] = ...) -> None: ...

class JoinConsumerGroupRequest(_message.Message):
    __slots__ = ("groupId", "consumerId", "streams")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    CONSUMERID_FIELD_NUMBER: _ClassVar[int]
    STREAMS_FIELD_NUMBER: _ClassVar[int]
    groupId: str
    consumerId: str
    streams: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        groupId: _Optional[str] = ...,
        consumerId: _Optional[str] = ...,
        streams: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class JoinConsumerGroupResponse(_message.Message):
    __slots__ = (
        "coordinator",
        "epoch",
        "consumerTimeout",
        "coordinatorTimeout",
    )
    COORDINATOR_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    CONSUMERTIMEOUT_FIELD_NUMBER: _ClassVar[int]
    COORDINATORTIMEOUT_FIELD_NUMBER: _ClassVar[int]
    coordinator: str
    epoch: int
    consumerTimeout: int
    coordinatorTimeout: int
    def __init__(
        self,
        coordinator: _Optional[str] = ...,
        epoch: _Optional[int] = ...,
        consumerTimeout: _Optional[int] = ...,
        coordinatorTimeout: _Optional[int] = ...,
    ) -> None: ...

class LeaveConsumerGroupRequest(_message.Message):
    __slots__ = ("groupId", "consumerId")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    CONSUMERID_FIELD_NUMBER: _ClassVar[int]
    groupId: str
    consumerId: str
    def __init__(
        self, groupId: _Optional[str] = ..., consumerId: _Optional[str] = ...
    ) -> None: ...

class LeaveConsumerGroupResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FetchConsumerGroupAssignmentsRequest(_message.Message):
    __slots__ = ("groupId", "consumerId", "epoch")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    CONSUMERID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    groupId: str
    consumerId: str
    epoch: int
    def __init__(
        self,
        groupId: _Optional[str] = ...,
        consumerId: _Optional[str] = ...,
        epoch: _Optional[int] = ...,
    ) -> None: ...

class PartitionAssignment(_message.Message):
    __slots__ = ("stream", "partitions")
    STREAM_FIELD_NUMBER: _ClassVar[int]
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    stream: str
    partitions: _containers.RepeatedScalarFieldContainer[int]
    def __init__(
        self,
        stream: _Optional[str] = ...,
        partitions: _Optional[_Iterable[int]] = ...,
    ) -> None: ...

class FetchConsumerGroupAssignmentsResponse(_message.Message):
    __slots__ = ("epoch", "assignments")
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    epoch: int
    assignments: _containers.RepeatedCompositeFieldContainer[
        PartitionAssignment
    ]
    def __init__(
        self,
        epoch: _Optional[int] = ...,
        assignments: _Optional[
            _Iterable[_Union[PartitionAssignment, _Mapping]]
        ] = ...,
    ) -> None: ...

class ReportConsumerGroupCoordinatorRequest(_message.Message):
    __slots__ = ("groupId", "consumerId", "coordinator", "epoch")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    CONSUMERID_FIELD_NUMBER: _ClassVar[int]
    COORDINATOR_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    groupId: str
    consumerId: str
    coordinator: str
    epoch: int
    def __init__(
        self,
        groupId: _Optional[str] = ...,
        consumerId: _Optional[str] = ...,
        coordinator: _Optional[str] = ...,
        epoch: _Optional[int] = ...,
    ) -> None: ...

class ReportConsumerGroupCoordinatorResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Broker(_message.Message):
    __slots__ = ("id", "host", "port", "partitionCount", "leaderCount")
    ID_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    PARTITIONCOUNT_FIELD_NUMBER: _ClassVar[int]
    LEADERCOUNT_FIELD_NUMBER: _ClassVar[int]
    id: str
    host: str
    port: int
    partitionCount: int
    leaderCount: int
    def __init__(
        self,
        id: _Optional[str] = ...,
        host: _Optional[str] = ...,
        port: _Optional[int] = ...,
        partitionCount: _Optional[int] = ...,
        leaderCount: _Optional[int] = ...,
    ) -> None: ...

class StreamMetadata(_message.Message):
    __slots__ = ("name", "subject", "error", "partitions", "creationTimestamp")
    class Error(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OK: _ClassVar[StreamMetadata.Error]
        UNKNOWN_STREAM: _ClassVar[StreamMetadata.Error]

    OK: StreamMetadata.Error
    UNKNOWN_STREAM: StreamMetadata.Error
    class PartitionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: PartitionMetadata
        def __init__(
            self,
            key: _Optional[int] = ...,
            value: _Optional[_Union[PartitionMetadata, _Mapping]] = ...,
        ) -> None: ...

    NAME_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    CREATIONTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    name: str
    subject: str
    error: StreamMetadata.Error
    partitions: _containers.MessageMap[int, PartitionMetadata]
    creationTimestamp: int
    def __init__(
        self,
        name: _Optional[str] = ...,
        subject: _Optional[str] = ...,
        error: _Optional[_Union[StreamMetadata.Error, str]] = ...,
        partitions: _Optional[_Mapping[int, PartitionMetadata]] = ...,
        creationTimestamp: _Optional[int] = ...,
    ) -> None: ...

class ConsumerGroupMetadata(_message.Message):
    __slots__ = ("groupId", "error", "coordinator", "epoch")
    class Error(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OK: _ClassVar[ConsumerGroupMetadata.Error]
        UNKNOWN_GROUP: _ClassVar[ConsumerGroupMetadata.Error]

    OK: ConsumerGroupMetadata.Error
    UNKNOWN_GROUP: ConsumerGroupMetadata.Error
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    COORDINATOR_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    groupId: str
    error: ConsumerGroupMetadata.Error
    coordinator: str
    epoch: int
    def __init__(
        self,
        groupId: _Optional[str] = ...,
        error: _Optional[_Union[ConsumerGroupMetadata.Error, str]] = ...,
        coordinator: _Optional[str] = ...,
        epoch: _Optional[int] = ...,
    ) -> None: ...

class PartitionEventTimestamps(_message.Message):
    __slots__ = ("firstTimestamp", "latestTimestamp")
    FIRSTTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LATESTTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    firstTimestamp: int
    latestTimestamp: int
    def __init__(
        self,
        firstTimestamp: _Optional[int] = ...,
        latestTimestamp: _Optional[int] = ...,
    ) -> None: ...

class PartitionMetadata(_message.Message):
    __slots__ = (
        "id",
        "leader",
        "replicas",
        "isr",
        "highWatermark",
        "newestOffset",
        "paused",
        "readonly",
        "messagesReceivedTimestamps",
        "pauseTimestamps",
        "readonlyTimestamps",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    LEADER_FIELD_NUMBER: _ClassVar[int]
    REPLICAS_FIELD_NUMBER: _ClassVar[int]
    ISR_FIELD_NUMBER: _ClassVar[int]
    HIGHWATERMARK_FIELD_NUMBER: _ClassVar[int]
    NEWESTOFFSET_FIELD_NUMBER: _ClassVar[int]
    PAUSED_FIELD_NUMBER: _ClassVar[int]
    READONLY_FIELD_NUMBER: _ClassVar[int]
    MESSAGESRECEIVEDTIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    PAUSETIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    READONLYTIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    id: int
    leader: str
    replicas: _containers.RepeatedScalarFieldContainer[str]
    isr: _containers.RepeatedScalarFieldContainer[str]
    highWatermark: int
    newestOffset: int
    paused: bool
    readonly: bool
    messagesReceivedTimestamps: PartitionEventTimestamps
    pauseTimestamps: PartitionEventTimestamps
    readonlyTimestamps: PartitionEventTimestamps
    def __init__(
        self,
        id: _Optional[int] = ...,
        leader: _Optional[str] = ...,
        replicas: _Optional[_Iterable[str]] = ...,
        isr: _Optional[_Iterable[str]] = ...,
        highWatermark: _Optional[int] = ...,
        newestOffset: _Optional[int] = ...,
        paused: bool = ...,
        readonly: bool = ...,
        messagesReceivedTimestamps: _Optional[
            _Union[PartitionEventTimestamps, _Mapping]
        ] = ...,
        pauseTimestamps: _Optional[
            _Union[PartitionEventTimestamps, _Mapping]
        ] = ...,
        readonlyTimestamps: _Optional[
            _Union[PartitionEventTimestamps, _Mapping]
        ] = ...,
    ) -> None: ...

class Message(_message.Message):
    __slots__ = (
        "offset",
        "key",
        "value",
        "timestamp",
        "stream",
        "partition",
        "subject",
        "replySubject",
        "headers",
        "ackInbox",
        "correlationId",
        "ackPolicy",
    )
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[bytes] = ...
        ) -> None: ...

    OFFSET_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    REPLYSUBJECT_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    ACKINBOX_FIELD_NUMBER: _ClassVar[int]
    CORRELATIONID_FIELD_NUMBER: _ClassVar[int]
    ACKPOLICY_FIELD_NUMBER: _ClassVar[int]
    offset: int
    key: bytes
    value: bytes
    timestamp: int
    stream: str
    partition: int
    subject: str
    replySubject: str
    headers: _containers.ScalarMap[str, bytes]
    ackInbox: str
    correlationId: str
    ackPolicy: AckPolicy
    def __init__(
        self,
        offset: _Optional[int] = ...,
        key: _Optional[bytes] = ...,
        value: _Optional[bytes] = ...,
        timestamp: _Optional[int] = ...,
        stream: _Optional[str] = ...,
        partition: _Optional[int] = ...,
        subject: _Optional[str] = ...,
        replySubject: _Optional[str] = ...,
        headers: _Optional[_Mapping[str, bytes]] = ...,
        ackInbox: _Optional[str] = ...,
        correlationId: _Optional[str] = ...,
        ackPolicy: _Optional[_Union[AckPolicy, str]] = ...,
    ) -> None: ...

class Ack(_message.Message):
    __slots__ = (
        "stream",
        "partitionSubject",
        "msgSubject",
        "offset",
        "ackInbox",
        "correlationId",
        "ackPolicy",
        "receptionTimestamp",
        "commitTimestamp",
        "ackError",
    )
    class Error(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OK: _ClassVar[Ack.Error]
        UNKNOWN: _ClassVar[Ack.Error]
        INCORRECT_OFFSET: _ClassVar[Ack.Error]
        TOO_LARGE: _ClassVar[Ack.Error]
        ENCRYPTION: _ClassVar[Ack.Error]

    OK: Ack.Error
    UNKNOWN: Ack.Error
    INCORRECT_OFFSET: Ack.Error
    TOO_LARGE: Ack.Error
    ENCRYPTION: Ack.Error
    STREAM_FIELD_NUMBER: _ClassVar[int]
    PARTITIONSUBJECT_FIELD_NUMBER: _ClassVar[int]
    MSGSUBJECT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    ACKINBOX_FIELD_NUMBER: _ClassVar[int]
    CORRELATIONID_FIELD_NUMBER: _ClassVar[int]
    ACKPOLICY_FIELD_NUMBER: _ClassVar[int]
    RECEPTIONTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    COMMITTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ACKERROR_FIELD_NUMBER: _ClassVar[int]
    stream: str
    partitionSubject: str
    msgSubject: str
    offset: int
    ackInbox: str
    correlationId: str
    ackPolicy: AckPolicy
    receptionTimestamp: int
    commitTimestamp: int
    ackError: Ack.Error
    def __init__(
        self,
        stream: _Optional[str] = ...,
        partitionSubject: _Optional[str] = ...,
        msgSubject: _Optional[str] = ...,
        offset: _Optional[int] = ...,
        ackInbox: _Optional[str] = ...,
        correlationId: _Optional[str] = ...,
        ackPolicy: _Optional[_Union[AckPolicy, str]] = ...,
        receptionTimestamp: _Optional[int] = ...,
        commitTimestamp: _Optional[int] = ...,
        ackError: _Optional[_Union[Ack.Error, str]] = ...,
    ) -> None: ...

class CreateStreamOp(_message.Message):
    __slots__ = ("stream", "partitions")
    STREAM_FIELD_NUMBER: _ClassVar[int]
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    stream: str
    partitions: _containers.RepeatedScalarFieldContainer[int]
    def __init__(
        self,
        stream: _Optional[str] = ...,
        partitions: _Optional[_Iterable[int]] = ...,
    ) -> None: ...

class DeleteStreamOp(_message.Message):
    __slots__ = ("stream",)
    STREAM_FIELD_NUMBER: _ClassVar[int]
    stream: str
    def __init__(self, stream: _Optional[str] = ...) -> None: ...

class PauseStreamOp(_message.Message):
    __slots__ = ("stream", "partitions", "resumeAll")
    STREAM_FIELD_NUMBER: _ClassVar[int]
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    RESUMEALL_FIELD_NUMBER: _ClassVar[int]
    stream: str
    partitions: _containers.RepeatedScalarFieldContainer[int]
    resumeAll: bool
    def __init__(
        self,
        stream: _Optional[str] = ...,
        partitions: _Optional[_Iterable[int]] = ...,
        resumeAll: bool = ...,
    ) -> None: ...

class ResumeStreamOp(_message.Message):
    __slots__ = ("stream", "partitions")
    STREAM_FIELD_NUMBER: _ClassVar[int]
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    stream: str
    partitions: _containers.RepeatedScalarFieldContainer[int]
    def __init__(
        self,
        stream: _Optional[str] = ...,
        partitions: _Optional[_Iterable[int]] = ...,
    ) -> None: ...

class SetStreamReadonlyOp(_message.Message):
    __slots__ = ("stream", "partitions", "readonly")
    STREAM_FIELD_NUMBER: _ClassVar[int]
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    READONLY_FIELD_NUMBER: _ClassVar[int]
    stream: str
    partitions: _containers.RepeatedScalarFieldContainer[int]
    readonly: bool
    def __init__(
        self,
        stream: _Optional[str] = ...,
        partitions: _Optional[_Iterable[int]] = ...,
        readonly: bool = ...,
    ) -> None: ...

class JoinConsumerGroupOp(_message.Message):
    __slots__ = ("groupId", "consumerId", "streams")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    CONSUMERID_FIELD_NUMBER: _ClassVar[int]
    STREAMS_FIELD_NUMBER: _ClassVar[int]
    groupId: str
    consumerId: str
    streams: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        groupId: _Optional[str] = ...,
        consumerId: _Optional[str] = ...,
        streams: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class LeaveConsumerGroupOp(_message.Message):
    __slots__ = ("groupId", "consumerId", "expired")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    CONSUMERID_FIELD_NUMBER: _ClassVar[int]
    EXPIRED_FIELD_NUMBER: _ClassVar[int]
    groupId: str
    consumerId: str
    expired: bool
    def __init__(
        self,
        groupId: _Optional[str] = ...,
        consumerId: _Optional[str] = ...,
        expired: bool = ...,
    ) -> None: ...

class ActivityStreamEvent(_message.Message):
    __slots__ = (
        "id",
        "op",
        "createStreamOp",
        "deleteStreamOp",
        "pauseStreamOp",
        "resumeStreamOp",
        "setStreamReadonlyOp",
        "joinConsumerGroupOp",
        "leaveConsumerGroupOp",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    OP_FIELD_NUMBER: _ClassVar[int]
    CREATESTREAMOP_FIELD_NUMBER: _ClassVar[int]
    DELETESTREAMOP_FIELD_NUMBER: _ClassVar[int]
    PAUSESTREAMOP_FIELD_NUMBER: _ClassVar[int]
    RESUMESTREAMOP_FIELD_NUMBER: _ClassVar[int]
    SETSTREAMREADONLYOP_FIELD_NUMBER: _ClassVar[int]
    JOINCONSUMERGROUPOP_FIELD_NUMBER: _ClassVar[int]
    LEAVECONSUMERGROUPOP_FIELD_NUMBER: _ClassVar[int]
    id: int
    op: ActivityStreamOp
    createStreamOp: CreateStreamOp
    deleteStreamOp: DeleteStreamOp
    pauseStreamOp: PauseStreamOp
    resumeStreamOp: ResumeStreamOp
    setStreamReadonlyOp: SetStreamReadonlyOp
    joinConsumerGroupOp: JoinConsumerGroupOp
    leaveConsumerGroupOp: LeaveConsumerGroupOp
    def __init__(
        self,
        id: _Optional[int] = ...,
        op: _Optional[_Union[ActivityStreamOp, str]] = ...,
        createStreamOp: _Optional[_Union[CreateStreamOp, _Mapping]] = ...,
        deleteStreamOp: _Optional[_Union[DeleteStreamOp, _Mapping]] = ...,
        pauseStreamOp: _Optional[_Union[PauseStreamOp, _Mapping]] = ...,
        resumeStreamOp: _Optional[_Union[ResumeStreamOp, _Mapping]] = ...,
        setStreamReadonlyOp: _Optional[
            _Union[SetStreamReadonlyOp, _Mapping]
        ] = ...,
        joinConsumerGroupOp: _Optional[
            _Union[JoinConsumerGroupOp, _Mapping]
        ] = ...,
        leaveConsumerGroupOp: _Optional[
            _Union[LeaveConsumerGroupOp, _Mapping]
        ] = ...,
    ) -> None: ...
