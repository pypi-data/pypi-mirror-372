"""Activity tracking resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.activity import Activity
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from ..client import SnailOrbitAsyncClient, SnailOrbitClient


class ActivityResource(BaseResource):
    """Synchronous activity tracking operations."""

    def __init__(self, client: SnailOrbitClient) -> None:
        """Initialize activity resource."""
        super().__init__(client)

    def list(
        self, start: float, end: float, user_id: str | None = None, **params: Any
    ) -> Iterator[Activity]:
        """List activities within a time range.

        Args:
            start: Start timestamp (Unix timestamp)
            end: End timestamp (Unix timestamp)
            user_id: Optional user ID to filter activities
            **params: Additional query parameters

        Yields:
            Activity objects
        """
        query_params = {'start': start, 'end': end, **params}
        if user_id is not None:
            query_params['user_id'] = user_id

        yield from self._paginate('/api/v1/activity/list', Activity, query_params)


class AsyncActivityResource(AsyncBaseResource):
    """Asynchronous activity tracking operations."""

    def __init__(self, client: SnailOrbitAsyncClient) -> None:
        """Initialize async activity resource."""
        super().__init__(client)

    async def list(
        self, start: float, end: float, user_id: str | None = None, **params: Any
    ) -> AsyncIterator[Activity]:
        """List activities within a time range.

        Args:
            start: Start timestamp (Unix timestamp)
            end: End timestamp (Unix timestamp)
            user_id: Optional user ID to filter activities
            **params: Additional query parameters

        Yields:
            Activity objects
        """
        query_params = {'start': start, 'end': end, **params}
        if user_id is not None:
            query_params['user_id'] = user_id

        async for activity in self._paginate(
            '/api/v1/activity/list', Activity, query_params
        ):
            yield activity
