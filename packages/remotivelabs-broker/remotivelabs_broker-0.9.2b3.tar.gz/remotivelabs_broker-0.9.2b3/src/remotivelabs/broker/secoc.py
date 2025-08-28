from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class SecocFreshnessValue:
    """
    Set SecOC binary freshness value to be used by freshness manager.
    Property is limited to SecOC on a given name space.
    """

    fv: bytes


@dataclass(frozen=True)
class SecocTimeDiff:
    """
    Set a time delta to use in real time clock for SecOC freshness value. Time
    difference is in floating point seconds and is limited to a name space.
    """

    time_diff: float


@dataclass(frozen=True)
class SecocKey:
    """
    Set binary 128-bit key to be used for SecOC in the RemotiveBroker.

    Multiple keys can be set and are separated by key ID's.
    """

    key_id: int
    key: bytes


@dataclass(frozen=True)
class SecocCmac0:
    """
    Use CMAC0 for SecOC in the RemotiveBroker.
    """

    enabled: bool


SecocProperty = Union[SecocFreshnessValue, SecocTimeDiff, SecocKey, SecocCmac0]
