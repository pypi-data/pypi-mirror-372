from __future__ import annotations

import grpc
import grpc.aio

import remotivelabs.broker.conv.grpc_converters as conv
from remotivelabs.broker._generated import (
    common_pb2,
    restbus_api_pb2,
    restbus_api_pb2_grpc,
)
from remotivelabs.broker.frame import FrameName
from remotivelabs.broker.namespace import NamespaceName
from remotivelabs.broker.restbus.signal_config import RestbusFrameConfig, RestbusSignalConfig
from remotivelabs.broker.signal import SignalName


class Restbus:
    _restbus_stub: restbus_api_pb2_grpc.RestbusServiceStub

    def __init__(self, channel: grpc.aio.Channel, client_name: str):
        self._restbus_stub = restbus_api_pb2_grpc.RestbusServiceStub(channel)
        self._client_name = client_name

    async def close(self, *namespace: NamespaceName) -> None:
        """
        Removes all configured signals and stops the Restbus on the specified namespace.

        Args:
            *namespace:
                One or more namespaces to close
        """

        await self._restbus_stub.Remove(restbus_api_pb2.RemoveRequest(namespaces=conv.namespace_to_grpc_namespaces(*namespace)))

    async def add(self, *frames: tuple[NamespaceName, list[RestbusFrameConfig]], start: bool = False):
        """
        Adds one or more frames to the Restbus with optional start flag.

        Args:
            *frames:
                One or more tuples, each containing namespace and list of frame configurations which should be added to the restbus
            start: If True, starts the frames after adding. Defaults to False.

        Note: The start flag affects all frames running on the namespace, even if they are added since before.
        """

        items = [
            restbus_api_pb2.FrameConfig(
                frameId=common_pb2.SignalId(name=frame.name, namespace=common_pb2.NameSpace(name=namespace)),
                cycleTime=frame.cycle_time,
            )
            for namespace, frame_configs in frames
            for frame in frame_configs
        ]
        await self._restbus_stub.Add(
            restbus_api_pb2.AddRequest(
                clientId=common_pb2.ClientId(id=self._client_name),
                frames=restbus_api_pb2.FrameConfigs(items=items),
                startOption=restbus_api_pb2.StartOption.START_AFTER_ADD if start else restbus_api_pb2.StartOption.NOP,
            )
        )

    async def start(self, *namespace: NamespaceName):
        """
        Starts Restbus signal publishing for the specified namespaces.

        Args:
            *namespace:
                One or more namespaces to start
        """
        await self._restbus_stub.Start(restbus_api_pb2.RestbusRequest(namespaces=conv.namespace_to_grpc_namespaces(*namespace)))

    async def stop(self, *namespace: NamespaceName):
        """
        Stops Restbus signal publishing for the specified namespaces.

        Args:
            *namespace:
                One or more namespaces to stop. A stopped restbus can be started again.
        """
        await self._restbus_stub.Stop(restbus_api_pb2.RestbusRequest(namespaces=conv.namespace_to_grpc_namespaces(*namespace)))

    async def remove(self, *frames: tuple[NamespaceName, list[FrameName]]):
        """
        Removes specific frames from the Restbus.

        Args:
            *frames:
                One or more tuples, each containing namespace and list of frame names to remove from the restbus
        """

        await self._restbus_stub.Remove(restbus_api_pb2.RemoveRequest(frameIds=conv.tuple_to_signal_ids(list(frames))))

    async def update_signals(self, *signals: tuple[NamespaceName, list[RestbusSignalConfig]]) -> None:
        """
        Updates the configured signals on the Restbus with new values.

        Args:
            *signals:
                One or more tuples, each containing namespace and list of signal configurations to apply to the restbus
        """
        await self._restbus_stub.Update(restbus_api_pb2.UpdateRequest(signals=conv.signal_configs_to_grpc(list(signals))))

    async def reset_signals(self, *signals: tuple[NamespaceName, list[SignalName]]) -> None:
        """
        Resets specified signals to their default configured values.

        Args:
            *signals:
                One or more tuples, each containing namespace and list of signal names to reset
        """

        await self._restbus_stub.Reset(restbus_api_pb2.ResetRequest(signalIds=conv.tuple_to_signal_ids(list(signals))))

    async def reset_namespaces(self, *namespace: NamespaceName) -> None:
        """
        Resets all configured namespaces and their associated signals to default values.
        Args:
            *namespace:
                One or more namespaces to reset
        """
        await self._restbus_stub.Reset(restbus_api_pb2.ResetRequest(namespaces=conv.namespace_to_grpc_namespaces(*namespace)))
