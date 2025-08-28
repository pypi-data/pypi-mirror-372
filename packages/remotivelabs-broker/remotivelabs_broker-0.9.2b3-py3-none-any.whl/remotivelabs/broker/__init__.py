"""
# RemotiveLabs Broker API
This module handles communication with the RemotiveBroker.

The RemotiveBroker can run locally or in RemotiveCloud. Connecting to a RemotiveCloud instance requires additional
authentication parameters—see the `remotivelabs.broker.auth` module for details.

## Installation

.. code-block:: bash
    pip install remotivelabs-broker

## Logging

This library uses Python's standard `logging` module. By default, the library does not configure any logging handlers,
allowing applications to fully control their logging setup.

To enable logs from this library in your application or tests, configure logging as follows:

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("remotivelabs.broker").setLevel(logging.DEBUG)
```

For more advanced configurations, refer to the [Python logging documentation](https://docs.python.org/3/library/logging.html).

"""

import logging

from remotivelabs.broker import auth, exceptions, recording_session, restbus
from remotivelabs.broker.__about__ import __version__
from remotivelabs.broker.client import BrokerClient
from remotivelabs.broker.frame import Frame, FrameInfo, FrameName, FrameSubscription, Header
from remotivelabs.broker.namespace import NamespaceInfo, NamespaceName
from remotivelabs.broker.restbus import RestbusFrameConfig, RestbusSignalConfig
from remotivelabs.broker.secoc import SecocCmac0, SecocFreshnessValue, SecocKey, SecocProperty, SecocTimeDiff
from remotivelabs.broker.signal import Signal, SignalInfo, SignalName, SignalValue, WriteSignal

__all__ = [
    "__version__",
    "auth",
    "exceptions",
    "recording_session",
    "restbus",
    "BrokerClient",
    "Frame",
    "FrameInfo",
    "FrameName",
    "FrameSubscription",
    "Header",
    "NamespaceInfo",
    "NamespaceName",
    "RestbusFrameConfig",
    "RestbusSignalConfig",
    "SecocCmac0",
    "SecocFreshnessValue",
    "SecocKey",
    "SecocProperty",
    "SecocTimeDiff",
    "Signal",
    "SignalInfo",
    "SignalName",
    "SignalValue",
    "WriteSignal",
]


logging.getLogger("remotivelabs.broker").addHandler(logging.NullHandler())
