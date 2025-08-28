"""Protocol definitions for type-safe contracts throughout the client library.

This module defines the core interfaces that decouple business logic from
concrete model implementations, enabling type-safe operations while preserving
flexibility for different data sources.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, TypeVar

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

# Generic type for model validation
T = TypeVar('T')


class SyncHttpTransport(Protocol):
    """Protocol for synchronous HTTP transport implementations."""

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make a synchronous HTTP request and return the response data."""
        ...

    def paginate(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        limit: int = 100,
    ) -> Iterator[Any]:
        """Paginate through API results synchronously."""
        ...


class AsyncHttpTransport(Protocol):
    """Protocol for asynchronous HTTP transport implementations."""

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make an asynchronous HTTP request and return the response data."""
        ...

    def paginate(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        limit: int = 100,
    ) -> AsyncIterator[Any]:
        """Paginate through API results asynchronously."""
        ...


# Union type for both transport types
HttpTransport = SyncHttpTransport | AsyncHttpTransport


class AuthProvider(Protocol):
    """Protocol for authentication providers."""

    def get_auth_header(
        self, method: str, path: str, params: dict[str, Any] | None = None
    ) -> str:
        """Generate authentication header for a request."""
        ...


class ModelValidator(Protocol):
    """Protocol for model validation and conversion."""

    def validate_model(self, data: Any, model_class: type[T]) -> T:
        """Validate raw data against a model class."""
        ...


# Note: This module focuses on transport, auth, and core client protocols


# Resource operation contracts


class ResourceOperations(Protocol):
    """Protocol for basic CRUD operations on resources."""

    async def get(self, entity_id: str) -> Any:
        """Get a single entity by ID."""
        ...

    def list(self, **params: Any) -> Iterator[Any] | AsyncIterator[Any]:
        """List entities with optional filtering."""
        ...

    async def create(self, data: dict[str, Any]) -> Any:
        """Create a new entity."""
        ...

    async def update(self, entity_id: str, data: dict[str, Any]) -> Any:
        """Update an existing entity."""
        ...

    async def delete(self, entity_id: str) -> None:
        """Delete an entity."""
        ...


class PaginatedResponse(Protocol):
    """Protocol for paginated API responses."""

    count: int
    limit: int
    offset: int
    items: list[Any]


# Configuration contracts


class ClientConfiguration(Protocol):
    """Protocol for client configuration."""

    timeout: float
    max_retries: int
    retry_delay: float
    rate_limit: int
    user_agent: str
    verify_ssl: bool


class HttpConfiguration(Protocol):
    """Protocol for HTTP-specific configuration."""

    pool_connections: int
    pool_maxsize: int
    max_redirects: int
