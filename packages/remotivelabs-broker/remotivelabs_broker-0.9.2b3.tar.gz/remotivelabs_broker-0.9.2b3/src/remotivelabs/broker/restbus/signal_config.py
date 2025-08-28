from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from remotivelabs.broker.frame import FrameName
from remotivelabs.broker.signal import SignalName, SignalValue


@dataclass
class RestbusFrameConfig:
    """
    Configuration for a frame in the Restbus.

    Attributes:
        name: The name of the frame to configure.
        cycle_time: Optional cycle time override for the frame. If None, the default from the broker's database is used.
    """

    name: FrameName
    cycle_time: float | None = None


@dataclass
class RestbusSignalConfig:
    """
    This class defines how a specific signal should behave when emitted by Restbus. A signal can have:

    Attributes:
        name: The name of the signal
        loop: Values emitted in order after the initial sequence
        initial: Optional values emitted once before the loop starts
    """

    name: SignalName
    loop: Sequence[SignalValue]
    initial: Sequence[SignalValue] = field(default_factory=list)

    @classmethod
    def set(cls, name: SignalName, value: SignalValue) -> RestbusSignalConfig:
        """
        Create a SignalConfig with a constant value.

        Args:
            name: Name of the signal
            value: Value to set in Restbus
        """
        return cls(name=name, loop=[value])

    @classmethod
    def set_update_bit(cls, name: SignalName) -> RestbusSignalConfig:
        """
        Create a SignalConfig for an update-bit pattern (sends 1 once, then constant 0).

        Args:
            name: Name of the signal
        """
        return cls(name=name, loop=[0], initial=[1])
