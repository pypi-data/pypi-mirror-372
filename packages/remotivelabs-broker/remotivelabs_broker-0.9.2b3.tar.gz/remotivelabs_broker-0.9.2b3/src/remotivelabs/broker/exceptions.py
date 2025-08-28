from dataclasses import dataclass


class BrokerError(Exception):
    """Raised for general RemotiveBroker errors"""


@dataclass
class BrokerLicenseError(BrokerError):
    """Raised for license errors"""

    host: str
    message: str

    def __str__(self):
        return f"invalid license for broker at {self.host}: {self.message}"


@dataclass
class BrokerConnectionError(BrokerError):
    """Raised for communication errors with a RemotiveBroker"""

    host: str
    message: str

    def __str__(self):
        return f"failed to connect to broker at {self.host}: {self.message}"
