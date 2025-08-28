from __future__ import annotations

import logging

import grpc
import grpc.aio
from typing_extensions import Self

from remotivelabs.broker._generated import (
    common_pb2,
    system_api_pb2,
    system_api_pb2_grpc,
)
from remotivelabs.broker.auth import AuthMethod, NoAuth
from remotivelabs.broker.exceptions import BrokerConnectionError, BrokerLicenseError
from remotivelabs.broker.interceptors import RequestInterceptor, StreamInterceptor
from remotivelabs.broker.params import create_random_client_id, get_connection_details_from_url

_logger = logging.getLogger(__name__)


def _create_insecure_channel(host: str) -> grpc.aio.Channel:
    return grpc.aio.insecure_channel(host)


def _create_secure_channel(host: str, auth: AuthMethod) -> grpc.aio.Channel:
    creds = grpc.ssl_channel_credentials()
    return grpc.aio.secure_channel(host, creds, interceptors=[RequestInterceptor(auth), StreamInterceptor(auth)])  # type: ignore


class BrokerClientConnection:
    """
    Represents a connection to a RemotiveBroker
    """

    _client_id: str
    _host: str
    _auth: AuthMethod
    url: str

    _channel: grpc.aio.Channel
    _system_service: system_api_pb2_grpc.SystemServiceStub

    _connected: bool

    def __init__(self, url: str, client_id: str | None = None, auth: AuthMethod = NoAuth()):
        """
        Initializes a connection to a RemotiveBroker. Not really useful as a standalone class, but useful for inheritance.

        Args:
            url: The RemotiveBroker URL to connect to.
            client_id: Optional client ID. If None, a random ID is generated.
            auth: Authentication method to use. Defaults to NoAuth.
        """
        if not url:
            raise ValueError("Missing broker URL")
        self.url = url
        self._client_id = client_id or create_random_client_id()
        self._host, use_tls = get_connection_details_from_url(self.url)
        self._auth = auth
        self._channel = _create_secure_channel(self._host, auth) if use_tls else _create_insecure_channel(self._host)

        self._system_service = system_api_pb2_grpc.SystemServiceStub(self._channel)

        self._connected = False

    @property
    def client_id(self) -> str:
        """The client id used by this client"""
        return self._client_id

    async def connect(self) -> Self:
        """
        Connect to the broker and verify license validity.
        This is an idempotent operation - calling it multiple times has no additional effect.

        Returns:
            The connected client instance.

        Raises:
            BrokerLicenseError: If the broker license is invalid.
            BrokerConnectionError: If connection to the broker fails.
        """
        if self._connected:
            return self
        try:
            valid = await self.check_license()
            if not valid:
                raise BrokerLicenseError(host=self._host, message="invalid license")
        except grpc.aio.AioRpcError as e:
            raise BrokerConnectionError(host=self._host, message=f"BrokerClient: {str(e)}") from e
        self._connected = True
        _logger.debug(f"connected to broker {self._host} using client id {self._client_id}")

        return self

    async def disconnect(self) -> None:
        """
        Disconnect the client from the broker and release all associated resources.

        This method is idempotent, subsequent calls after the first have no effect.
        Once disconnected, the client can no longer be used.
        """
        if self._connected:
            await self._channel.close(None)
            _logger.debug(f"{self._client_id} disconnected from broker {self._host}")
            self._connected = False

    async def __aenter__(self) -> Self:
        return await self.connect()

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.disconnect()

    def _get_state(self) -> grpc.ChannelConnectivity:
        return self._channel.get_state()

    async def check_license(self) -> bool:
        """
        Check if the broker license is valid.

        Returns:
            True if the broker license is valid, otherwise False.
        """
        info: system_api_pb2.LicenseInfo = await self._system_service.GetLicenseInfo(common_pb2.Empty())
        return info.status == system_api_pb2.LicenseStatus.VALID
