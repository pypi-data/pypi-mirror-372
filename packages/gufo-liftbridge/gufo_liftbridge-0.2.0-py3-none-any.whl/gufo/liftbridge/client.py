# ----------------------------------------------------------------------
# Python Liftbridge client
# ----------------------------------------------------------------------
# Copyright (C) 2022-25, Gufo Labs
# See LICENSE.md for details
# ----------------------------------------------------------------------

"""
Python Liftbridge client.

Attributes:
    logger: Client logger.
"""

# Python modules
import asyncio
import logging
import random
import socket
from types import TracebackType
from typing import (
    Any,
    AsyncIterable,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
)

# Third-party modules
from grpc import ChannelConnectivity, StatusCode  # type:ignore[import-untyped]
from grpc.aio import (  # type:ignore[import-untyped]
    AioRpcError,
    insecure_channel,
)

from .api_pb2 import (
    Ack,
    CreateStreamRequest,
    DeleteStreamRequest,
    FetchCursorRequest,
    FetchMetadataRequest,
    FetchMetadataResponse,
    FetchPartitionMetadataRequest,
    PublishRequest,
    SetCursorRequest,
    SubscribeRequest,
)

# Gufo Liftbridge modules
from .api_pb2_grpc import APIStub
from .compressor import compress, decompress
from .error import (
    ErrorChannelClosed,
    ErrorMessageSizeExceeded,
    ErrorNoMetadataLeader,
    ErrorNotFound,
    ErrorUnavailable,
    LiftbridgeError,
    rpc_error,
)
from .types import (
    AckPolicy,
    Broker,
    Message,
    Metadata,
    PartitionMetadata,
    StartPosition,
    StreamMetadata,
)
from .utils import is_ipv4

logger = logging.getLogger("gufo.liftbridge")


CURSOR_STREAM = "__cursors"
DEFAULT_MAX_MESSAGE_SIZE = 16 * 1024 * 1024
BROKER_PARTS = 2


class GRPCChannel(object):
    """
    gRPC channel wrapper. Wraps connection to broker.

    Args:
        broker: target address in form "<address>:<port>".
    """

    def __init__(self, broker: str) -> None:
        self.broker = broker
        self.channel = None
        self.stub: Optional[APIStub] = None

    def __getattr__(self, item: str) -> Callable[..., Any]:
        """Get wrapped API method."""
        return getattr(self.stub, item)  # type: ignore[no-any-return]

    async def __aenter__(self) -> "GRPCChannel":
        """Context manager enter."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        """Context management exit."""
        await self.close()
        return None

    async def connect(
        self,
        max_message_size: int = DEFAULT_MAX_MESSAGE_SIZE,
        enable_http_proxy: bool = False,
    ) -> None:
        """
        Connect channel.

        Args:
            max_message_size: Maximal size of message.
            enable_http_proxy: Enable usage of HTTP proxies.
        """
        self.channel = insecure_channel(
            self.broker,
            options=[
                (
                    "grpc.max_send_message_length",
                    max_message_size,
                ),
                (
                    "grpc.max_receive_message_length",
                    max_message_size,
                ),
                (
                    "grpc.enable_http_proxy",
                    enable_http_proxy,
                ),
            ],
        )
        while True:
            logger.debug("[%s] Connecting", self.broker)
            try:
                await self._wait_for_channel_ready()
            except ErrorUnavailable as e:
                logger.debug("[%s] Failed to connect: %s", self.broker, e)
                await asyncio.sleep(1)
                continue
            logger.debug("[%s] Channel is ready", self.broker)
            self.stub = APIStub(self.channel)  # type:ignore[no-untyped-call]
            return

    async def close(self) -> None:
        """Close channel connection."""
        if not self.channel:
            return
        logger.debug("[%s] Closing channel", self.broker)
        await self.channel.close()
        self.channel = None
        self.stub = None

    async def _wait_for_channel_ready(self) -> None:
        """
        Wait until channel became ready.

        Raises:
            ErrorUnavailable: if broker is not available.
            RuntimeError: If channel is not set.
        """
        if not self.channel:
            msg = "channel must be set"
            raise RuntimeError(msg)
        while True:
            state = self.channel.get_state(try_to_connect=True)
            if state == ChannelConnectivity.READY:
                return
            if state in (
                ChannelConnectivity.TRANSIENT_FAILURE,
                ChannelConnectivity.SHUTDOWN,
            ):
                raise ErrorUnavailable("Unavailable: %s" % state)
            await self.channel.wait_for_state_change(state)


class LiftbridgeClient(object):
    """
    Asynchronous Liftbridge client.

    Args:
        brokers: Iterable of stings containning hints to cluster
            members, either as FQDN or in `<address>:<port>` format.
        max_message_size: Maximal size of message in octets.
        enable_http_proxy: Enable usage of HTTP proxies.
        compression_method: Enable message compression.
        compression_threshold: Works only if `compression_method` is set.
            Do not compress messages with size below
            the `compression_threshold`.
        encoding_header: Header name to pass `compression_method` when
            message is compressed.
        publish_async_ack_timeout:
        metadata_leader_timeout: Mean timeout on `no metadata leader` error.
        metadata_leader_dev: Deviation of timeout on
            `no metadata leader` error.

    Raises:
        ValueError: If parameters are incorrect.
    """

    GRPC_RESTARTABLE_CODES = frozenset(
        (
            StatusCode.UNAVAILABLE,
            StatusCode.FAILED_PRECONDITION,
            StatusCode.NOT_FOUND,
            StatusCode.INTERNAL,
        )
    )

    def __init__(
        self,
        brokers: Iterable[str],
        *,
        max_message_size: int = DEFAULT_MAX_MESSAGE_SIZE,
        enable_http_proxy: bool = False,
        compression_method: Optional[str] = None,
        compression_threshold: int = 0,
        encoding_header: str = "X-Msg-Encoding",
        publish_async_ack_timeout: float = 10.0,
        metadata_leader_timeout: float = 3.0,
        metadata_leader_dev: float = 1.0,
    ) -> None:
        self.broker_seeds = list(brokers)
        if not self.broker_seeds:
            msg = "Empty broker seeds"
            raise ValueError(msg)
        # Check seeds
        for seed in self.broker_seeds:
            if not self._is_broker_addr(seed):
                msg = f"Invalid broker seed: {seed}"
                raise ValueError(msg)
        self.max_message_size = max_message_size
        self.enable_http_proxy = enable_http_proxy
        self.compression_method = compression_method
        self.compression_threshold = compression_threshold
        self.encoding_header = encoding_header
        self.publish_async_ack_timeout = publish_async_ack_timeout
        self.metadata_leader_timeout = metadata_leader_timeout
        self.metadata_leader_dev = metadata_leader_dev
        self.channels: Dict[str, GRPCChannel] = {}  # broker -> GRPCChannel
        self.open_brokers: List[str] = []
        # (stream, partition) -> broker
        self.leaders: Dict[Tuple[str, int], str] = {}
        # (stream, partition) -> [broker, ...]
        self.isrs: Dict[Tuple[str, int], List[str]] = {}

    @staticmethod
    def _is_broker_addr(broker: str) -> bool:
        """
        Check if string is valid broker address.

        Args:
            broker: Broker address string

        Returns:
            `True`, if `broker` is valid address, `False` otherwise.
        """
        parts = broker.split(":")
        if len(parts) != BROKER_PARTS:
            return False
        # Check port
        try:
            int(parts[1])
        except ValueError:
            return False
        return True

    async def _close_channel(self, broker: str) -> None:
        """
        Close broker channel.

        Args:
            broker: Broker address in form "<address>:<port>"
        """
        ch = self.channels[broker]
        await ch.close()
        del self.channels[broker]
        self.open_brokers = list(self.channels)

    async def close(self) -> None:
        """Close all open channels."""
        for broker in list(self.channels):
            await self._close_channel(broker)

    async def __aenter__(self) -> "LiftbridgeClient":
        """Entering context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit from context manager."""
        await self.close()
        return None

    async def _get_seed(self) -> str:
        """
        Get first resolvable seed.

        Returns:
            Broker address in form `<addreess>:<port>`

        Raises:
            ErrorNotFound: When failed to resolve all seeds.
        """
        seeds = self.broker_seeds.copy()
        random.shuffle(seeds)
        # Process until first resolvable seed
        for seed in seeds:
            parts = seed.split(":")
            try:
                host = await self._resolve(parts[0])
                return f"{host}:{parts[1]}"
            except ErrorNotFound:
                continue
        msg = "Cannot resolve any seeds"
        raise ErrorNotFound(msg)

    async def _get_channel(self, broker: Optional[str] = None) -> GRPCChannel:
        """
        Get GRPC channel for a broker.

        Use random broker from seed if the broker is not set.

        Args:
            broker: Broker address in "<address>:<port>" format.

        Returns:
            Open gRPC channel

        Raises:
            ErrorNotFound: On resolver failure.
        """
        if not broker:
            if self.channels:
                # Use random existing channel
                broker = random.choice(self.open_brokers)  # noqa:S311
            else:
                broker = await self._get_seed()
        channel = self.channels.get(broker)
        if not channel:
            channel = GRPCChannel(broker)
            await channel.connect(
                max_message_size=self.max_message_size,
                enable_http_proxy=self.enable_http_proxy,
            )
            self.channels[broker] = channel
            self.open_brokers = list(self.channels)
        return channel

    @staticmethod
    async def _sleep_on_error(
        delay: float = 1.0, deviation: float = 0.5
    ) -> None:
        """
        Wait random time on error.

        Args:
            delay: Average delay in seecods.
            deviation: Deviation from delay in seconds.
        """
        r = random.random()  # noqa:S311
        await asyncio.sleep(delay - deviation + 2 * deviation * r)

    async def _get_leader(self, stream: str, partition: int) -> str:
        """
        Get leader broker for partition.

        Args:
            stream: Stream name.
            partition: Partition number.

        Returns:
            Broker address for partition leader.
        """
        if not self.leaders:
            await self._refresh_leaders()
        p_id = (stream, partition)
        while True:
            leader = self.leaders.get(p_id)
            if leader:
                return leader
            logger.debug(
                "Leader for %s:%s is not available still. Waiting",
                stream,
                partition,
            )
            await asyncio.sleep(1)  # @todo: Configurable
            await self._refresh_leaders()

    async def _get_leader_channel(
        self, stream: str, partition: int
    ) -> GRPCChannel:
        """
        Get GRPCChannel for partition leader.

        Args:
            stream: Stream name.
            partition: Partition number.

        Returns:
            Open GRPCChanel
        """
        broker = await self._get_leader(stream, partition)
        return await self._get_channel(broker)

    async def _resolve(
        self, host: str, cache: Optional[Dict[str, List[str]]] = None
    ) -> str:
        """
        Resolve host name to IP address.

        Args:
            host: FQDN or IP addreess.
            cache: Optional dict to cache results.

        Returns:
            Resolved IP address.

        Raises:
            ErrorNotFound: On resolution failure.
        """
        if is_ipv4(host):
            return host
        # Resolve from cache
        addrs = cache.get(host) if cache else None
        if not addrs:
            # Resolve hostname
            try:
                addr_info = await asyncio.get_running_loop().getaddrinfo(
                    host, None, proto=socket.IPPROTO_TCP
                )
                addrs = [x[4][0] for x in addr_info if x[0] == socket.AF_INET]
                if cache is not None:
                    cache[host] = addrs
            except socket.gaierror as e:
                msg = f"Cannot resolve broker address: {host}"
                raise ErrorNotFound(msg) from e
        return random.choice(addrs)  # noqa:S311

    async def _update_topology(self, r: FetchMetadataResponse) -> None:
        """
        Update partition leaders information from FetchMetadata response.

        Args:
            r: FetchMetadataResponse instance
        """
        # Resolver cache
        r_cache: Dict[str, List[str]] = {}
        # Resolve brokers
        brokers: Dict[str, str] = {}  # id -> host:port
        for b in r.brokers:
            host = await self._resolve(b.host, r_cache)
            brokers[b.id] = "%s:%s" % (host, b.port)
        # Update leaders
        self.leaders = {}
        for m in r.streamMetadata:
            for p in m.partitions.values():
                if not p.leader:
                    logger.debug("%s:%s has no leader still", m.name, p.id)
                leader = brokers.get(p.leader)
                if not leader:
                    logger.error(
                        "%s:%s uses unknown leader broker %s",
                        m.name,
                        p.id,
                        p.leader,
                    )
                    continue
                self.leaders[m.name, p.id] = leader
                self.isrs[m.name, p.id] = []
                for isr in p.isr:
                    broker = brokers.get(isr)
                    if not broker:
                        logger.error(
                            "%s:%s uses unknown isr broker %s",
                            m.name,
                            p.id,
                            isr,
                        )
                        continue
                    self.isrs[m.name, p.id] += [broker]
        # Close channels for a left brokers
        for broker in set(self.channels) - set(brokers.values()):
            logger.debug("[%s] Closing left broker", broker)
            await self._close_channel(broker)

    async def _refresh_leaders(self) -> None:
        """Refresh cluster partition leaders."""
        logger.info("Refresh leaders")
        await self.get_metadata(wait_for_stream=True)

    def _reset_leaders(self) -> None:
        """Clean up cluster partition leaders."""
        self.leaders = {}

    async def get_metadata(
        self, stream: Optional[str] = None, *, wait_for_stream: bool = False
    ) -> Metadata:
        """
        Get cluster metadata.

        Args:
            stream: Fetch metadata only for particular stream, if set.
            wait_for_stream: Wait until stream will be created.
        """
        req = FetchMetadataRequest()
        if stream:
            req.streams.append(stream)
        while True:
            channel = await self._get_channel()
            try:
                r: FetchMetadataResponse = await channel.FetchMetadata(req)
            except AioRpcError as e:
                logger.info("Failed to get metadata: %s", e)
                if e.code() in self.GRPC_RESTARTABLE_CODES:
                    await self._sleep_on_error(
                        delay=self.metadata_leader_timeout,
                        deviation=self.metadata_leader_dev,
                    )
                    continue
                raise e
            if not r.streamMetadata and wait_for_stream:
                await asyncio.sleep(1)
                continue
            await self._update_topology(r)
            return Metadata(
                brokers=[
                    Broker(id=b.id, host=b.host, port=b.port)
                    for b in r.brokers
                ],
                metadata=[
                    StreamMetadata(
                        name=m.name,
                        subject=m.subject,
                        partitions={
                            p.id: PartitionMetadata(
                                id=p.id,
                                leader=p.leader,
                                replicas=list(p.replicas),
                                isr=list(p.isr),
                                high_watermark=p.highWatermark,
                                newest_offset=p.newestOffset,
                                paused=p.paused,
                            )
                            for p in m.partitions.values()
                        },
                    )
                    for m in r.streamMetadata
                ],
            )

    async def get_partition_metadata(
        self, stream: str, partition: int, wait_for_stream: bool = False
    ) -> PartitionMetadata:
        """
        Fetch metadata for particular partition.

        Args:
            stream: Stream name.
            partition: Partitionn number.
            wait_for_stream: If set, wait for stream being available.

        Returns:
            Partition metadata.
        """
        while True:
            channel = await self._get_leader_channel(stream, partition)
            r = await channel.FetchPartitionMetadata(
                FetchPartitionMetadataRequest(
                    stream=stream, partition=partition
                )
            )
            if not r.metadata and wait_for_stream:
                await asyncio.sleep(1)
                continue
            p = r.metadata
            return PartitionMetadata(
                id=p.id,
                leader=p.leader,
                replicas=list(p.replicas),
                isr=list(p.isr),
                high_watermark=p.highWatermark,
                newest_offset=p.newestOffset,
                paused=p.paused,
            )

    async def create_stream(
        self,
        name: str,
        *,
        subject: Optional[str] = None,
        group: Optional[str] = None,
        replication_factor: int = 1,
        minisr: int = 0,
        partitions: int = 1,
        enable_compact: bool = False,
        retention_max_age: int = 0,
        retention_max_bytes: int = 0,
        segment_max_age: int = 0,
        segment_max_bytes: int = 0,
        auto_pause_time: int = 0,
        auto_pause_disable_if_subscribers: bool = False,
        wait_for_stream: bool = False,
    ) -> None:
        """
        Create stream. Internal implementation.

        Args:
            name: Stream name.
            subject: Optional NATS subject.
            group: ???
            replication_factor: Replication factor, amount of
                cluster members to replicate each partition.
            minisr: Minimum in-service replicas.
            partitions: Number of partition in the stream.
            enable_compact: Enable stream compaction.
            retention_max_age: ???
            retention_max_bytes: ???
            segment_max_age: ???
            segment_max_bytes: ???
            auto_pause_time: ???
            auto_pause_disable_if_subscribers: ???
            wait_for_stream: Wait until the stream is really created.
        """
        req = CreateStreamRequest(
            subject=subject or name,
            name=name,
            group=group,
            replicationFactor=replication_factor,
            partitions=partitions,
        )
        if enable_compact:
            req.compactEnabled.value = True
        else:
            req.compactEnabled.value = False
        if minisr:
            req.minIsr.value = minisr
        # Retention settings
        if retention_max_age:
            # in ms
            req.retentionMaxAge.value = retention_max_age * 1000
        if retention_max_bytes:
            req.retentionMaxBytes.value = retention_max_bytes
        # Segment settings
        if segment_max_bytes:
            req.segmentMaxBytes.value = segment_max_bytes
        if segment_max_age:
            # in ms
            req.segmentMaxAge.value = segment_max_age * 1000
        if auto_pause_time:
            req.autoPauseTime.value = auto_pause_time * 1000
            if auto_pause_disable_if_subscribers:
                req.autoPauseDisableIfSubscribers.value = True
        channel = await self._get_channel()
        while True:
            try:
                with rpc_error():
                    await channel.CreateStream(req)
                    break
            except ErrorNoMetadataLeader:
                logger.info("No metadata leader, retrying.")
                await self._sleep_on_error(
                    delay=self.metadata_leader_timeout,
                    deviation=self.metadata_leader_dev,
                )
        if wait_for_stream:
            await self.get_metadata(name, wait_for_stream=True)

    async def delete_stream(self, name: str) -> None:
        """
        Delete streeam.

        Args:
            name: Stream name.
        """
        with rpc_error():
            channel = await self._get_channel()
            await channel.DeleteStream(DeleteStreamRequest(name=name))

    def get_publish_request(
        self,
        value: bytes,
        *,
        stream: Optional[str] = None,
        key: Optional[bytes] = None,
        partition: Optional[int] = None,
        headers: Optional[Dict[str, bytes]] = None,
        ack_inbox: Optional[str] = None,
        correlation_id: Optional[str] = None,
        ack_policy: AckPolicy = AckPolicy.LEADER,
        auto_compress: bool = False,
    ) -> PublishRequest:
        """
        Generate PublishRequest for bulk operations.

        Args:
            value: Message body.
            stream: Stream to publish.
            key: Optional message key.
            partition: Partition.
            headers: Message headers.
            ack_inbox: Optional inbox to send acknowledge.
            correlation_id: Opaque id to correlate messages.
            ack_policy: Acknowledgement policies.
            auto_compress: If `True` compress value if the
                client's `compression_method` is set
                and the size of value is beyound `compression_threshold`.
        """
        to_compress = (
            auto_compress
            and self.compression_method is not None
            and len(value) >= self.compression_threshold
        )
        if to_compress and self.compression_method is not None:
            value = compress(value, self.compression_method)
        # Publish Request
        req = PublishRequest(value=value, ackPolicy=ack_policy.value)
        if stream:
            req.stream = stream
        if key is not None:
            req.key = key
        if partition is not None:
            req.partition = partition
        if to_compress and self.compression_method:
            req.headers[self.encoding_header] = self.compression_method.encode(
                "utf-8"
            )
        if headers:
            for h, v in headers.items():
                req.headers[h] = v
        if ack_inbox:
            req.ackInbox = ack_inbox
        if correlation_id:
            req.correlationId = correlation_id
        return req

    async def _publish(
        self, req: PublishRequest, wait_for_stream: bool = False
    ) -> None:
        """
        Send publish request and wait for acknowledge.

        Args:
            req: PublishRequest, result of `get_publish_request`.
            wait_for_stream: If `True`, wait until stream will be ready.
        """
        # Publish
        while True:
            channel = await self._get_channel()
            try:
                with rpc_error():
                    await channel.Publish(req)
                    break
            except ErrorUnavailable:
                await self._close_channel(channel.broker)
                logger.info(
                    "Loosing connection to current cluster member. "
                    "Trying to reconnect"
                )
                await asyncio.sleep(1)
            except ErrorMessageSizeExceeded as e:
                logger.error("Message size exceeded. Skipping... : %s", e)
                # @todo: Wait for Gufo Perf
                # metrics["liftbridge_publish_size_exceeded"] += 1
                break
            except ErrorNotFound as e:
                if wait_for_stream:
                    await self._close_channel(channel.broker)
                    logger.info(
                        "Stream '%s/%s' is not available yet. "
                        "Maybe election in progress. "
                        "Trying to reconnect to: %s:%s",
                        req.stream,
                        req.partition,
                        channel.broker,
                        channel,
                    )
                    await asyncio.sleep(1)
                else:
                    raise ErrorNotFound(str(e)) from e  # Reraise

    async def publish_bulk(
        self, iter_req: Iterable[PublishRequest], wait: bool = True
    ) -> AsyncIterable[Ack]:
        """
        Bulk publishing from iterator.

        Args:
            iter_req: Iterable of PublishRequest.
            wait: Wait for all acks if set to `True`.
        """

        async def drain_wait() -> AsyncIterable[PublishRequest]:
            nonlocal balance, done  # type: ignore[misc]
            for req in iter_req:
                balance += 1
                yield req
            done = asyncio.Event()
            await asyncio.wait_for(done.wait(), self.publish_async_ack_timeout)

        balance: int = 0
        done: Optional[asyncio.Event] = None
        with rpc_error():
            channel = await self._get_channel()
            async for ack in channel.PublishAsync(
                drain_wait() if wait else iter_req
            ):
                balance -= 1
                if done is not None and not balance:
                    done.set()
                yield ack

    async def publish(
        self,
        value: bytes,
        *,
        stream: Optional[str] = None,
        key: Optional[bytes] = None,
        partition: Optional[int] = None,
        headers: Optional[Dict[str, bytes]] = None,
        ack_inbox: Optional[str] = None,
        correlation_id: Optional[str] = None,
        ack_policy: AckPolicy = AckPolicy.LEADER,
        wait_for_stream: bool = False,
        auto_compress: bool = False,
    ) -> None:
        """
        Publish single message.

        Args:
            value: bytes,
            stream: Optional[str] = None,
            key: Optional[bytes] = None,
            partition: Optional[int] = None,
            headers: Optional[Dict[str, bytes]] = None,
            ack_inbox: Optional[str] = None,
            correlation_id: Optional[str] = None,
            ack_policy: AckPolicy = AckPolicy.LEADER,
            wait_for_stream: bool = False,
            auto_compress: bool = False,
        """
        # Build message
        req = self.get_publish_request(
            value,
            stream=stream,
            key=key,
            partition=partition,
            headers=headers,
            ack_inbox=ack_inbox,
            correlation_id=correlation_id,
            ack_policy=ack_policy,
            auto_compress=auto_compress,
        )
        # Publish
        await self._publish(req, wait_for_stream=wait_for_stream)

    async def subscribe(
        self,
        stream: str,
        *,
        partition: Optional[int] = None,
        start_position: StartPosition = StartPosition.NEW_ONLY,
        start_offset: Optional[int] = None,
        start_timestamp: Optional[float] = None,
        resume: bool = False,
        cursor_id: Optional[str] = None,
        timeout: Optional[int] = None,
        allow_isr: bool = False,
    ) -> AsyncIterable[Message]:
        """
        Subscribe to partition.

        Args:
            stream: Stream name.
            partition: Stream partition.
            start_position: Starting position. See `StartPosition` for details.
            start_offset: Starting offset, if `start_position` is `OFFSET`
            start_timestamp: Starting timestamp,
                if `start_position` is `TIMESTAMP`
            resume: Resume start position.
            cursor_id: Cursor ID to resume, if `start_position` is `RESUME`.
            timeout: Optional timeout in seconds.
            allow_isr: Allow connections to in-state replicas (ISR).
        """
        # Build request
        req = SubscribeRequest(stream=stream)
        to_restore_position = start_position == StartPosition.RESUME
        if partition is not None:
            req.partition = partition
        if resume:
            req.resume = resume
        if allow_isr:
            req.readISRReplica = True
        if start_offset is not None:
            req.startPosition = StartPosition.OFFSET.value
            req.startOffset = start_offset
        elif start_timestamp is not None:
            req.startPosition = StartPosition.TIMESTAMP.value
            req.startTimestamp = int(start_timestamp * 1_000_000_000.0)
        elif start_position == StartPosition.RESUME:
            if not cursor_id:
                msg = "cursor_id must be set for StartPosition.RESUME"
                raise ValueError(msg)
            logger.debug("Getting stored offset for stream '%s'", stream)
            req.startPosition = StartPosition.OFFSET.value
            logger.debug("Resuming from offset %d", req.startOffset)
        else:
            req.startPosition = start_position  # type:ignore[assignment]
        to_recover: bool = (
            False  # Recover flag. Set if client from LiftbridgeError recover
        )
        last_offset: Optional[int] = None
        while True:
            try:
                async for message in self._subscribe(
                    req,
                    restore_position=to_restore_position,
                    cursor_id=cursor_id,
                    to_recover=to_recover,
                ):
                    yield message
                    last_offset = message.offset
            except ErrorUnavailable as e:
                logger.error(
                    "Subscriber looses connection to partition node: %s", e
                )
                logger.info("Reconnecting")
                self._reset_leaders()
                await self._sleep_on_error()
                if not to_restore_position and last_offset is not None:
                    # Continue from last seen position
                    req.startPosition = StartPosition.OFFSET.value
                    req.startOffset = last_offset + 1
                    to_restore_position = False
            except LiftbridgeError as e:
                logger.error("Subscriber channel was unknown error: %s", e)
                logger.info("Try to continue from last offset")
                if not to_restore_position and last_offset is not None:
                    # Continue from last seen position
                    req.startPosition = StartPosition.OFFSET.value
                    req.startOffset = last_offset + 1
                    to_restore_position = False
                    to_recover = True
                # For cluster problem recommended 30 second wait
                await self._sleep_on_error(delay=30, deviation=10)

    async def _subscribe(
        self,
        req: SubscribeRequest,
        restore_position: bool = False,
        cursor_id: Optional[str] = None,
        to_recover: bool = False,
    ) -> AsyncIterable[Message]:
        """Internal implementation for subscribe."""
        allow_isr = bool(req.readISRReplica)
        with rpc_error():
            broker: Optional[str] = None
            if allow_isr:
                isrs = self.isrs.get((req.stream, req.partition))
                if isrs:
                    broker = random.choice(isrs)  # noqa: S311
            if not broker:
                broker = await self._get_leader(req.stream, req.partition)
            async with GRPCChannel(broker) as channel:
                logger.debug(
                    "[%s] Subscribing stream '%s'", broker, req.stream
                )
                if restore_position and cursor_id:
                    req.startOffset = await self.get_cursor(
                        stream=req.stream,
                        partition=req.partition,
                        cursor_id=cursor_id,
                    )
                if req.startOffset:
                    logger.debug(
                        "[%s] Resuming from position %d",
                        broker,
                        req.startOffset,
                    )
                call = channel.Subscribe(req)
                # NB: We cannot use `async for msg in call` construction
                # Due to liftbridge protocol specific:
                # --- CUT ---
                # When the subscription stream is created,
                # the server sends an empty message
                # to indicate the subscription was successfully created.
                # Otherwise, an error is sent on the stream
                # if the subscribe failed. This handshake message
                # must be handled and should not be exposed to the user.
                # --- CUT ---
                # So grpc aio implementation treats first message as aio.EOF
                # and hangs forever trying to get error status from core.
                # So we use own inlined `_fetch_stream_responses`
                # implementation here
                msg = await call._read()
                logger.debug(
                    "[%s] Stream is ready, waiting for messages", broker
                )
                # Next, process all other messages
                msg = await call._read()
                to_recover = False  # clean if message successful get
                while msg:
                    value = msg.value
                    headers = msg.headers
                    if self.encoding_header in headers:
                        comp = headers.pop(self.encoding_header).decode(
                            "utf-8"
                        )
                        value = decompress(value, comp)
                    yield Message(
                        value=value,
                        subject=msg.subject,
                        offset=msg.offset,
                        timestamp=msg.timestamp,
                        key=msg.key,
                        partition=msg.partition,
                        headers=headers,
                    )
                    msg = await call._read()
                # Get core message to explain the result
                code = await call.code()
                detail = await call.debug_error_string()
                if code in self.GRPC_RESTARTABLE_CODES:
                    raise ErrorUnavailable()
                if code == StatusCode.UNKNOWN and not to_recover:
                    raise LiftbridgeError(str(detail))
                raise ErrorChannelClosed(str(code))

    async def wait_for_stream(self, stream: str) -> None:
        """
        Wait until stream become availabble.

        Args:
            stream: Stream name
        """
        await self.get_metadata(stream, wait_for_stream=True)

    async def wait_for_cursors(self) -> None:
        """Wait until cursors become available."""
        await self.wait_for_stream(CURSOR_STREAM)

    async def get_cursor(
        self, stream: str, partition: int, cursor_id: str
    ) -> int:
        """
        Fetch current partition cursor position.

        Args:
            stream: Stream name.
            partition: Partition numbers.
            cursor_id: Cursor identifier.

        Returns:
            Current cursor position. -1 for the new cursor.
        """
        with rpc_error():
            while True:
                channel = await self._get_leader_channel(CURSOR_STREAM, 0)
                try:
                    r = await channel.FetchCursor(
                        FetchCursorRequest(
                            stream=stream,
                            partition=partition,
                            cursorId=cursor_id,
                        )
                    )
                except AioRpcError as e:
                    logger.info("Failed to get cursor: %s", e)
                    if e.code() in self.GRPC_RESTARTABLE_CODES:
                        self._reset_leaders()
                        await self._sleep_on_error()
                        continue
                    raise e
                v = r.offset or 0
                logger.debug(
                    "Fetching cursor %s for %s:%s: current value is %s",
                    cursor_id,
                    stream,
                    partition,
                    v,
                )
                return v

    async def set_cursor(
        self, stream: str, partition: int, cursor_id: str, offset: int
    ) -> None:
        """
        Save cursor position for partition.

        Args:
            stream: Stream name.
            partition: Partition number.
            cursor_id: Cursor identifier.
            offset: Cursor offset to save.
        """
        with rpc_error():
            while True:
                try:
                    channel = await self._get_leader_channel(CURSOR_STREAM, 0)
                    await channel.SetCursor(
                        SetCursorRequest(
                            stream=stream,
                            partition=partition,
                            cursorId=cursor_id,
                            offset=offset + 1,
                        )
                    )
                    return
                except AioRpcError as e:
                    logger.info("Failed to set cursor: %s", e)
                    if e.code() in self.GRPC_RESTARTABLE_CODES:
                        self._reset_leaders()
                        await self._sleep_on_error()
                        continue
                    raise e
