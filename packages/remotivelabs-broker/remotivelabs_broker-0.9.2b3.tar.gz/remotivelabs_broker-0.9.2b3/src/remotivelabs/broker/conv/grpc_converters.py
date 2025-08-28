from __future__ import annotations

from remotivelabs.broker import signal
from remotivelabs.broker._generated import common_pb2, network_api_pb2, restbus_api_pb2, system_api_pb2
from remotivelabs.broker.frame import FrameInfo, FrameName
from remotivelabs.broker.namespace import NamespaceInfo, NamespaceName
from remotivelabs.broker.restbus.signal_config import RestbusSignalConfig
from remotivelabs.broker.secoc import SecocCmac0, SecocFreshnessValue, SecocKey, SecocProperty, SecocTimeDiff
from remotivelabs.broker.signal import Signal, SignalInfo, SignalName, SignalValue, WriteSignal


def value_to_network_value(v: SignalValue) -> network_api_pb2.Value:
    if signal.is_int(v):
        return network_api_pb2.Value(integer=v)
    if signal.is_float(v):
        return network_api_pb2.Value(double=v)
    if signal.is_binary(v):
        return network_api_pb2.Value(raw=v)
    return network_api_pb2.Value(strValue=v)


def tuple_to_signal_ids(items: list[tuple[NamespaceName, list[str]]]) -> network_api_pb2.SignalIds:
    return network_api_pb2.SignalIds(
        signalId=[
            common_pb2.SignalId(name=name, namespace=common_pb2.NameSpace(name=namespace)) for namespace, names in items for name in names
        ]
    )


# Namespace Conversions
def namespace_to_grpc(namespace: NamespaceName | NamespaceInfo) -> common_pb2.NameSpace:
    return common_pb2.NameSpace(name=namespace.name) if isinstance(namespace, NamespaceInfo) else common_pb2.NameSpace(name=namespace)


def namespace_to_grpc_namespaces(*namespace: NamespaceName) -> network_api_pb2.SignalIds:
    return common_pb2.Namespaces(items=[namespace_to_grpc(ns) for ns in namespace])


def signal_info_to_grpc(signal_info: SignalInfo) -> network_api_pb2.SignalIds:
    return common_pb2.SignalId(name=signal_info.name, namespace=common_pb2.NameSpace(name=signal_info.namespace))


def signal_infos_to_grpc(signal_infos: list[SignalInfo]) -> network_api_pb2.SignalIds:
    return network_api_pb2.SignalIds(signalId=[signal_info_to_grpc(signal_info) for signal_info in signal_infos])


def grpc_to_namespace_info(network_info: common_pb2.NetworkInfo) -> NamespaceInfo:
    return NamespaceInfo(name=network_info.namespace.name, type=network_info.type)


# Frame Conversions
def grpc_to_frame_info(frame_info: common_pb2.FrameInfo) -> FrameInfo:
    return FrameInfo(
        name=frame_info.signalInfo.id.name,
        namespace=frame_info.signalInfo.id.namespace.name,
        signals={signal.id.name: grpc_to_signal_info(signal) for signal in frame_info.childInfo},
        sender=frame_info.signalInfo.metaData.sender,
        receiver=frame_info.signalInfo.metaData.receiver,
        cycle_time_millis=frame_info.signalInfo.metaData.cycleTime,
    )


# Signal Conversions
def write_signal_to_grpc(namespace: NamespaceName, write_signal: WriteSignal) -> network_api_pb2.Signal:
    return network_api_pb2.Signal(
        id=common_pb2.SignalId(name=write_signal.name, namespace=common_pb2.NameSpace(name=namespace)),
        raw=write_signal.value if isinstance(write_signal.value, bytes) else None,
        integer=write_signal.value if isinstance(write_signal.value, int) else None,
        double=write_signal.value if isinstance(write_signal.value, float) else None,
        strValue=write_signal.value if isinstance(write_signal.value, str) else None,
    )


def signals_to_grpc(signals: list[Signal]) -> network_api_pb2.Signals:
    return network_api_pb2.Signals(
        signal=[
            network_api_pb2.Signal(
                id=common_pb2.SignalId(name=signal.name, namespace=common_pb2.NameSpace(name=signal.namespace)),
                raw=signal.value if isinstance(signal.value, bytes) else None,
                integer=signal.value if isinstance(signal.value, int) else None,
                double=signal.value if isinstance(signal.value, float) else None,
                strValue=signal.value if isinstance(signal.value, str) else None,
            )
            for signal in signals
        ]
    )


def grpc_to_signal(signal: network_api_pb2.Signal) -> Signal:
    value: int | float | bytes | str = signal.double
    if signal.raw != b"":
        value = signal.raw
    elif signal.HasField("integer"):
        value = signal.integer
    elif signal.HasField("strValue"):
        value = signal.strValue
    return Signal(
        name=signal.id.name,
        namespace=signal.id.namespace.name,
        value=value,
    )


def grpc_frame_to_signal_info(frame_info: common_pb2.FrameInfo) -> SignalInfo:
    return grpc_to_signal_info(frame_info.signalInfo)


def grpc_to_signal_info(signal_info: common_pb2.SignalInfo) -> SignalInfo:
    return SignalInfo(
        name=signal_info.id.name,
        namespace=signal_info.id.namespace.name,
        sender=signal_info.metaData.sender,
        receiver=signal_info.metaData.receiver,
        named_values=signal_info.metaData.namedValues,
        value_names={name: value for value, name in signal_info.metaData.namedValues.items()},
        min=signal_info.metaData.min,
        max=signal_info.metaData.max,
        factor=signal_info.metaData.factor,
    )


# Property Conversions
def property_to_grpc(namespace: NamespaceName, prop: SecocProperty) -> system_api_pb2.PropertyValue:
    if isinstance(namespace, NamespaceInfo):
        namespace = namespace.name
    if isinstance(prop, SecocFreshnessValue):
        return system_api_pb2.PropertyValue(name="secoc_fv", scope=[namespace], raw=prop.fv)
    if isinstance(prop, SecocTimeDiff):
        return system_api_pb2.PropertyValue(name="secoc_timediff", scope=[namespace], double=prop.time_diff)
    if isinstance(prop, SecocKey):
        return system_api_pb2.PropertyValue(name="secoc_key", scope=[namespace, str(prop.key_id)], raw=prop.key)
    if isinstance(prop, SecocCmac0):
        return system_api_pb2.PropertyValue(name="secoc_cmac0", scope=[namespace], integer=1 if prop.enabled else 0)
    raise TypeError(f"Unsupported SecocProperty type: {type(prop).__name__}")


# Configuration Conversions
def write_signal_to_grpc_publisher_config(
    items: list[tuple[NamespaceName, list[WriteSignal]]], client_id: str
) -> network_api_pb2.PublisherConfig:
    signal_list = [write_signal_to_grpc(namespace, value) for namespace, values in items for value in values]
    return network_api_pb2.PublisherConfig(
        clientId=common_pb2.ClientId(id=client_id),
        signals=network_api_pb2.Signals(signal=signal_list),
    )


def header_to_grpc_publisher_config(items: list[tuple[NamespaceName, list[FrameName]]], client_id: str) -> network_api_pb2.PublisherConfig:
    signal_list = [
        network_api_pb2.Signal(id=common_pb2.SignalId(name=name, namespace=common_pb2.NameSpace(name=namespace)), arbitration=True)
        for namespace, names in items
        for name in names
    ]
    return network_api_pb2.PublisherConfig(
        clientId=common_pb2.ClientId(id=client_id),
        signals=network_api_pb2.Signals(signal=signal_list),
    )


def signal_ids_to_grpc_subscriber_config(
    signals: list[tuple[NamespaceName, list[SignalName]]], client_id: str, on_change: bool, initial_empty: bool = False
) -> network_api_pb2.SubscriberConfig:
    return network_api_pb2.SubscriberConfig(
        clientId=common_pb2.ClientId(id=client_id), signals=tuple_to_signal_ids(signals), onChange=on_change, initialEmpty=initial_empty
    )


def signal_configs_to_grpc(items: list[tuple[NamespaceName, list[RestbusSignalConfig]]]) -> list[restbus_api_pb2.SignalSequence]:
    return [
        restbus_api_pb2.SignalSequence(
            id=common_pb2.SignalId(name=signal_config.name, namespace=namespace_to_grpc(namespace)),
            loop=[value_to_network_value(v) for v in signal_config.loop],
            initial=[value_to_network_value(v) for v in signal_config.initial],
        )
        for namespace, signal_configs in items
        for signal_config in signal_configs
    ]
