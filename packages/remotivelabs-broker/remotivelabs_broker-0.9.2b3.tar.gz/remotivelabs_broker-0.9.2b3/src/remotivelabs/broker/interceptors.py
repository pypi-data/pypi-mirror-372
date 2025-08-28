"""
Interceptors are a grpcio feature that allows to intercept messages before they are sent or received. We use it to append authentication
headers to the requests when authenticating with cloud brokers.
"""

from typing import Any, Callable

from grpc.aio import ClientCallDetails, Metadata, UnaryStreamClientInterceptor, UnaryUnaryClientInterceptor

from remotivelabs.broker.auth import AuthMethod, NoAuth
from remotivelabs.broker.exceptions import BrokerError


class AuthenticationInterceptorBase:
    def __init__(self, auth: AuthMethod) -> None:
        if isinstance(auth, NoAuth):
            raise BrokerError("You must supply credentials to use a secure channel (for e.g. cloud broker)")
        self._metadata = Metadata.from_tuple(auth.headers) if auth.headers else Metadata()  # type: ignore

    @property
    def metadata(self) -> Metadata:
        return self._metadata


class RequestInterceptor(AuthenticationInterceptorBase, UnaryUnaryClientInterceptor):
    def __init__(self, auth: AuthMethod) -> None:
        AuthenticationInterceptorBase.__init__(self, auth)

    async def intercept_unary_unary(self, continuation: Callable, client_call_details: ClientCallDetails, request: Any) -> Any:
        new_details = ClientCallDetails(
            method=client_call_details.method,
            timeout=client_call_details.timeout,
            metadata=self.metadata,
            credentials=client_call_details.credentials,
            wait_for_ready=client_call_details.wait_for_ready,
        )
        return await continuation(new_details, request)


class StreamInterceptor(AuthenticationInterceptorBase, UnaryStreamClientInterceptor):
    def __init__(self, auth: AuthMethod) -> None:
        AuthenticationInterceptorBase.__init__(self, auth)

    async def intercept_unary_stream(self, continuation: Callable, client_call_details: ClientCallDetails, request: Any) -> Any:
        new_details = ClientCallDetails(
            method=client_call_details.method,
            timeout=client_call_details.timeout,
            metadata=self.metadata,
            credentials=client_call_details.credentials,
            wait_for_ready=client_call_details.wait_for_ready,
        )
        return await continuation(new_details, request)
