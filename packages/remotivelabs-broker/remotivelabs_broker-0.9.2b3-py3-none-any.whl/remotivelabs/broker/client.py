from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import AsyncIterator

import grpc
import grpc.aio

import remotivelabs.broker.conv.grpc_converters as conv
from remotivelabs.broker._generated import (
    common_pb2,
    network_api_pb2,
    network_api_pb2_grpc,
    recordingsession_api_pb2_grpc,
    traffic_api_pb2_grpc,
)
from remotivelabs.broker.auth import AuthMethod, NoAuth
from remotivelabs.broker.connection import BrokerClientConnection
from remotivelabs.broker.frame import Frame, FrameInfo, FrameName, FrameSubscription, Header
from remotivelabs.broker.namespace import NamespaceInfo, NamespaceName
from remotivelabs.broker.restbus.restbus import Restbus
from remotivelabs.broker.secoc import SecocProperty
from remotivelabs.broker.signal import Signal, SignalInfo, SignalName, SignalValue, WriteSignal

_logger = logging.getLogger(__name__)


class BrokerClient(BrokerClientConnection):
    """
    Client for signal-related operations.
    """

    _network_service: network_api_pb2_grpc.NetworkServiceStub
    _traffic_service: traffic_api_pb2_grpc.TrafficServiceStub
    _recording_session_service: recordingsession_api_pb2_grpc.RecordingSessionServiceStub
    _cache: dict[str, common_pb2.Frames]
    _namespace_cache = dict[str, NamespaceInfo]
    restbus: Restbus

    def __init__(self, url: str, client_id: str | None = None, auth: AuthMethod = NoAuth()):
        """
        Initializes a new BrokerClient instance.

        Args:
            url: The RemotiveBroker URL to connect to.
            client_id: Optional client ID. If None, a random ID is generated.
            auth: Authentication method to use. Defaults to NoAuth.

        Note:
            Start the instance using a context manager:
            ```python
            async with BrokerClient(...) as client:
                ...
            ```

            Or use the connect/disconnect methods directly:
            ```python
            client = await BrokerClient(...).connect()
            # ...
            await client.disconnect()
            ```
        """
        super().__init__(url=url, client_id=client_id, auth=auth)

        self._network_service = network_api_pb2_grpc.NetworkServiceStub(self._channel)
        self._traffic_service = traffic_api_pb2_grpc.TrafficServiceStub(self._channel)
        self._recording_session_service = recordingsession_api_pb2_grpc.RecordingSessionServiceStub(self._channel)
        self.restbus = Restbus(self._channel, self._client_id)
        self._cache = defaultdict(str)
        self._namespace_cache = defaultdict(str)

    async def read_signals(self, *values: tuple[NamespaceName, list[str]]) -> list[Signal]:
        """
        Read signals from signal cache

        Args:
            *values:
                One or more tuples, each containing a namespace and a list of signal names of the signals to read.

        Raises:
            ValueError: If the list of values is empty.
        """

        if not values:
            raise ValueError("No signals provided")
        signals = await self._network_service.ReadSignals(conv.tuple_to_signal_ids(list(values)))
        return [conv.grpc_to_signal(signal) for signal in signals.signal if not signal.HasField("arbitration")]

    async def publish(self, *values: tuple[NamespaceName, list[WriteSignal]]) -> None:
        """
        Publish a list of signals to the broker.

        Args:
            *values:
                One or more tuples, each containing a namespace and a list of signals to publish.

        Raises:
            ValueError: If the list of values is empty.
        """

        if not values:
            raise ValueError("No signals provided")

        publisher_info = conv.write_signal_to_grpc_publisher_config(list(values), self.client_id)
        await self._network_service.PublishSignals(publisher_info)

    async def publish_header(self, *headers: tuple[NamespaceName, list[FrameName]]) -> None:
        """
        Publish a list of headers to the broker.

        Args:
            *headers:
                One or more tuples, each containing a namespace and a list of frame names of which headers to publish.

        Raises:
            ValueError: If the list of values is empty.
        """

        if not headers:
            raise ValueError("No signals provided")

        publisher_info = conv.header_to_grpc_publisher_config(list(headers), self.client_id)
        await self._network_service.PublishSignals(publisher_info)

    async def subscribe(
        self,
        *signals: tuple[NamespaceName, list[SignalName]],
        on_change: bool = False,
        initial_empty: bool = False,
    ) -> AsyncIterator[list[Signal]]:
        """
        Subscribe to a list of signals.

        Args:
            *signals:
                One or more tuples, each containing namespace and list of signals to subscribe to.
            on_change: Whether to receive updates only on change.
            initial_empty: True will wait until the broker has sent an initial message

        Returns:
            An asynchronous iterator of lists of Signal objects.
        """
        if not signals:
            raise ValueError("No subscription info provided")

        config = conv.signal_ids_to_grpc_subscriber_config(signals, self.client_id, on_change, initial_empty)
        stream = self._network_service.SubscribeToSignals(config)
        if initial_empty:
            # TODO: replace with anext(stream) when Python 3.9 is dropped
            async for _ in stream:
                break

        async def async_generator() -> AsyncIterator[list[Signal]]:
            async for signal_batch in stream:
                signals = [conv.grpc_to_signal(signal) for signal in signal_batch.signal if not signal.HasField("arbitration")]
                if signals:
                    yield signals

        return async_generator()

    async def subscribe_header(
        self,
        *headers: tuple[NamespaceName, list[FrameName]],
        initial_empty: bool = False,
    ) -> AsyncIterator[Header]:
        """
        Subscribe to a headers.

        Args:
            *headers:
                One or more tuples, each containing namespace and list of frame names of which headers to subscribe to.
            initial_empty: True will wait until the broker has sent an initial message

        Returns:
            An asynchronous iterator of of Header objects.
        """
        if not headers:
            raise ValueError("No subscription info provided")

        config = conv.signal_ids_to_grpc_subscriber_config(headers, self.client_id, False, initial_empty)
        stream = self._network_service.SubscribeToSignals(config)
        if initial_empty:
            # TODO: replace with anext(stream) when Python 3.9 is dropped
            async for _ in stream:
                break

        async def async_generator() -> AsyncIterator[Header]:
            async for signal_batch in stream:
                signal: network_api_pb2.Signal
                for signal in signal_batch.signal:
                    if signal.HasField("arbitration") and signal.arbitration:
                        yield Header(
                            frame_name=signal.id.name,
                            namespace=signal.id.namespace.name,
                        )

        return async_generator()

    async def subscribe_frames(
        self,
        *frames: tuple[NamespaceName, list[FrameSubscription]],
        on_change: bool = False,
        initial_empty: bool = False,
        decode_named_values: bool = False,
    ) -> AsyncIterator[Frame]:
        """
        Subscribe to a Frames.

        Args:
            *frames:
                One or more tuples, each containing namespace and list of frames to subscribe to.
            on_change: Whether to receive updates only on change.
            initial_empty: True will wait until the broker has sent an initial message
            decode_named_values: True will decode named values to str.

        Returns:
            An asynchronous iterator with Frames.
        """
        if not frames:
            raise ValueError("No subscription info provided")

        signal_ids, signal_meta, frame_keys = await self._collect_subscription_metadata(list(frames))
        config = conv.signal_ids_to_grpc_subscriber_config(list(signal_ids.items()), self.client_id, on_change, initial_empty)
        stream = self._network_service.SubscribeToSignals(config)

        if initial_empty:
            async for _ in stream:
                break

        async def async_generator():
            async for batch in stream:
                signals = [conv.grpc_to_signal(sig) for sig in batch.signal if not sig.HasField("arbitration")]
                if not signals:
                    continue

                frame = next((s for s in signals if (s.namespace, s.name) in frame_keys), None)
                if not frame:
                    _logger.warning(f"Frame not found in {signals}")
                    continue

                def decode(s: Signal) -> SignalValue:
                    meta = signal_meta.get((s.namespace, frame.name, s.name))
                    if decode_named_values and isinstance(s.value, int):
                        return meta.named_values.get(s.value, s.value)

                    return s.value

                yield Frame(
                    timestamp=batch.signal[0].timestamp,
                    name=frame.name,
                    namespace=frame.namespace,
                    signals={s.name: decode(s) for s in signals if s.name != frame.name},
                    value=frame.value,
                )

        return async_generator()

    async def set_secoc_property(self, namespace: NamespaceName | NamespaceInfo, property: SecocProperty) -> None:
        """
        Set a SecOC property on the broker.

        Args:
            namespace: Target namespace
            property: The SecOC property to set.
        """

        property_value = conv.property_to_grpc(namespace, property)
        await self._system_service.SetProperty(property_value)

    async def list_namespaces(self) -> list[NamespaceInfo]:
        """
        List all namespaces configured in the broker.

        Returns:
            A list of namespaces.
        """
        namespaces = await self._get_namespaces()
        return list(namespaces.values())

    async def get_namespace(self, name: NamespaceName) -> NamespaceInfo | None:
        """
        Get a namespace by name.

        Returns:
            The namespace if found, otherwise None.
        """
        namespaces = await self._get_namespaces()
        return namespaces.get(name)

    async def list_frame_infos(self, *namespaces: NamespaceName | NamespaceInfo) -> list[FrameInfo]:
        """
        List all frame infos in one or more namespaces.

        Args:
            namespaces: One or more NamespaceName or NamespaceInfo objects.

        Returns:
            A list of FrameInfo objects.
        """
        rets = await asyncio.gather(*(self._list_frame_infos(namespace) for namespace in namespaces))

        return [conv.grpc_to_frame_info(frame) for ret in rets for frame in ret.frame]

    async def get_frame_info(self, name: FrameName, namespace: NamespaceName | NamespaceInfo) -> FrameInfo | None:
        """
        Get a frame by name in a specific namespace.

        Args:
            name: The name of the frame.
            namespace: The namespace name or NamespaceInfo object.

        Returns:
            The FrameInfo object if found, otherwise None.
        """
        frames = await self.list_frame_infos(namespace)
        for frame in frames:
            if frame.name == name:
                return frame
        return None

    async def list_signal_infos(self, *namespaces: NamespaceName | NamespaceInfo) -> list[SignalInfo]:
        """
        List all signal infos in one or more namespaces.

        Args:
            namespaces: One or more NamespaceName or NamespaceInfo objects.

        Returns:
            A list of SignalInfo objects.
        """
        rets = await asyncio.gather(*(self._list_frame_infos(namespace) for namespace in namespaces))

        all_signals = []
        for ret in rets:
            frames_as_signals = [conv.grpc_frame_to_signal_info(frame) for frame in ret.frame]
            signals = [conv.grpc_to_signal_info(child) for frame in ret.frame for child in frame.childInfo]
            all_signals.extend(frames_as_signals + signals)

        return all_signals

    async def get_signal_info(self, name: SignalName, namespace: NamespaceName | NamespaceInfo) -> SignalInfo | None:
        """
        Get a signal info by name in a specific namespace.

        Args:
            name: The name of the signal.
            namespace: The namespace name or NamespaceInfo object.

        Returns:
            The SignalInfo object if found, otherwise None.
        """
        signals = await self.list_signal_infos(namespace)
        for signal in signals:
            if signal.name == name:
                return signal
        return None

    def is_ready(self) -> bool:
        """
        Check if the broker client is ready.

        Returns:
            True if the broker client is ready, otherwise False.
        """
        return self._get_state() == grpc.ChannelConnectivity.READY

    def is_closed(self) -> bool:
        """
        Check if the broker client is closed.

        Returns:
            True if the broker client is closed, otherwise False.
        """
        return self._get_state() == grpc.ChannelConnectivity.SHUTDOWN

    async def _collect_subscription_metadata(
        self,
        frames: list[tuple[NamespaceName, list[FrameSubscription]]],
    ) -> tuple[
        dict[NamespaceName, set[SignalName]],
        dict[tuple[NamespaceName, FrameName, SignalName], SignalInfo],
        set[tuple[NamespaceName, FrameName]],
    ]:
        signal_ids = defaultdict(set)
        signal_meta = {}
        frame_keys = set()

        for ns, subs in frames:
            for sub in subs:
                info = await self.get_frame_info(sub.name, ns)
                if not info:
                    _logger.warning(f"Frame not found in {sub.name}")
                    continue
                sigs = list(info.signals) if sub.signals is None else sub.signals
                signal_ids[ns].update([sub.name] + sigs)
                frame_keys.add((ns, sub.name))
                for s in sigs:
                    if s in info.signals:
                        signal_meta[(ns, sub.name, s)] = info.signals[s]

        return signal_ids, signal_meta, frame_keys

    async def _list_frame_infos(self, namespace: NamespaceName | NamespaceInfo) -> common_pb2.Frames:
        if isinstance(namespace, NamespaceInfo):
            namespace = namespace.name
        if namespace not in self._cache:
            self._cache[namespace] = await self._system_service.ListSignals(conv.namespace_to_grpc(namespace))
        return self._cache[namespace]

    async def _get_namespaces(self) -> dict[str, NamespaceInfo]:
        if len(self._namespace_cache) == 0:
            configs = await self._system_service.GetConfiguration(common_pb2.Empty())
            for ns in [conv.grpc_to_namespace_info(info) for info in configs.networkInfo]:
                self._namespace_cache[ns.name] = ns

        return self._namespace_cache
