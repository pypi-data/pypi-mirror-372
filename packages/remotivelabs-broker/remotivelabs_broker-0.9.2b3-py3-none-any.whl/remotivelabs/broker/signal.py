from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from typing_extensions import TypeIs

from remotivelabs.broker.namespace import NamespaceName

__doc__ = "Structures and types to work with signals"

SignalName = str
SignalValue = Union[int, float, bytes, str]
"""Valid value types for signals"""


@dataclass(frozen=True)
class Signal:
    """
    A signal with its name, namespace, and current value.

    Attributes:
        name: The name of the signal.
        namespace: The namespace the signal belongs to.
        value: The current value of the signal.
    """

    name: SignalName
    namespace: NamespaceName
    value: SignalValue

    def __str__(self) -> str:
        return f"{self.namespace}.{self.name}: {self.value!r}"


@dataclass(frozen=True)
class WriteSignal:
    """
    A signal intended to be published with a specific value.

    Attributes:
        name: The name of the signal to write.
        value: The value to assign to the signal.
    """

    name: SignalName
    value: SignalValue

    def __str__(self) -> str:
        return f"{self.name}: {self.value!r}"


@dataclass(frozen=True)
class SignalInfo:
    """
    Metadata describing a signal

    Attributes:
        name: Name of the signal.
        namespace: Namespace the signal belongs to.
        receiver: List of receivers for the signal.
        sender: List of senders for the signal.
        named_values: Mapping from raw numeric values to symbolic names (e.g., enums).
        value_names: Reverse mapping from symbolic names to raw numeric values.
        min: Minimum allowed value.
        max: Maximum allowed value.
        factor: Multiplication faction used for encoding and decoding value in frame.
    """

    name: SignalName
    namespace: NamespaceName
    receiver: list[str]
    sender: list[str]
    named_values: dict[int, str]
    value_names: dict[str, int]
    min: float
    max: float
    factor: float

    def __str__(self) -> str:
        return f"{self.namespace}.{self.name}"


def is_int(v: SignalValue) -> TypeIs[int]:
    return isinstance(v, int)


def is_float(v: SignalValue) -> TypeIs[float]:
    return isinstance(v, float)


def is_binary(v: SignalValue) -> TypeIs[bytes]:
    return isinstance(v, bytes)


def is_str(v: SignalValue) -> TypeIs[str]:
    return isinstance(v, str)
