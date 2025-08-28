from __future__ import annotations

from abc import ABC, abstractmethod


class AuthMethod(ABC):
    """Represents ways of authenticating to the Broker"""

    @abstractmethod
    def __str__(self) -> str:
        """Return the auth value as a string"""

    @property
    @abstractmethod
    def headers(self) -> list[tuple[str, str]] | None:
        """Return HTTP authentication headers"""


class NoAuth(AuthMethod):
    """No authentication method needed"""

    def __str__(self) -> str:
        return ""

    @property
    def headers(self) -> None:
        return None


class ApiKeyAuth(AuthMethod):
    """Api key authentication method (legacy)"""

    def __init__(self, api_key: str):
        self._api_key = api_key

    def __str__(self) -> str:
        return self._api_key

    @property
    def headers(self) -> list[tuple[str, str]]:
        return [("x-api-key", str(self))]


class TokenAuth(AuthMethod):
    """Token based authentication method"""

    def __init__(self, token: str):
        self._token = token

    def __str__(self) -> str:
        return self._token

    @property
    def headers(self) -> list[tuple[str, str]]:
        return [("authorization", f"Bearer {str(self)}"), ("x-api-key", str(self))]
