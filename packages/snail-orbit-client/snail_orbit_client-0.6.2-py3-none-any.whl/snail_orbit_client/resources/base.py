"""Base resource classes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from ..client import SnailOrbitAsyncClient, SnailOrbitClient

T = TypeVar('T', bound=BaseModel)


class BaseResource:
    """Base resource class for sync operations."""

    def __init__(self, client: SnailOrbitClient) -> None:
        """Initialize resource with client."""
        self.client = client

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make a GET request."""
        return self.client.get(path, params)

    def _post(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """Make a POST request."""
        return self.client.post(path, json_data=data)

    def _put(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """Make a PUT request."""
        return self.client.put(path, json_data=data)

    def _delete(self, path: str) -> Any:
        """Make a DELETE request."""
        return self.client.delete(path)

    def _validate_and_convert(self, data: Any, model_class: type[T]) -> T:
        """Validate and convert data to model."""
        return model_class.model_validate(data)

    def _paginate(
        self, path: str, model_class: type[T], params: dict[str, Any] | None = None
    ) -> Iterator[T]:
        """Paginate through results and convert to models."""
        for item in self.client.paginate(path, params):
            yield self._validate_and_convert(item, model_class)


class AsyncBaseResource:
    """Base resource class for async operations."""

    def __init__(self, client: SnailOrbitAsyncClient) -> None:
        """Initialize resource with async client."""
        self.client = client

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make an async GET request."""
        return await self.client.get(path, params)

    async def _post(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """Make an async POST request."""
        return await self.client.post(path, json_data=data)

    async def _put(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """Make an async PUT request."""
        return await self.client.put(path, json_data=data)

    async def _delete(self, path: str) -> Any:
        """Make an async DELETE request."""
        return await self.client.delete(path)

    def _validate_and_convert(self, data: Any, model_class: type[T]) -> T:
        """Validate and convert data to model."""
        return model_class.model_validate(data)

    async def _paginate(
        self, path: str, model_class: type[T], params: dict[str, Any] | None = None
    ) -> AsyncIterator[T]:
        """Async paginate through results and convert to models."""
        async for item in self.client.paginate(path, params):
            yield self._validate_and_convert(item, model_class)
