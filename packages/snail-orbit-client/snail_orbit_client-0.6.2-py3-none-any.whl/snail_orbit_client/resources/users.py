"""User management resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import UserFullOutput
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from ..client import SnailOrbitAsyncClient, SnailOrbitClient


class UsersResource(BaseResource):
    """Synchronous user management operations."""

    def __init__(self, client: SnailOrbitClient) -> None:
        """Initialize users resource."""
        super().__init__(client)

    def list(
        self, search: str | None = None, filter: str | None = None, **params: Any
    ) -> Iterator[UserFullOutput]:
        """List all users.

        Args:
            search: Search query to filter users
            filter: Filter query using query language (e.g., "name___contains:john and is_active___eq:true")
            **params: Other query parameters

        Yields:
            UserFullOutput objects
        """
        if search:
            params['search'] = search
        if filter:
            params['filter'] = filter
        yield from self._paginate('/api/v1/user/list', UserFullOutput, params)

    def get(self, user_id: str) -> UserFullOutput:
        """Get a specific user by ID.

        Args:
            user_id: User ID

        Returns:
            UserFullOutput object
        """
        data = self._get(f'/api/v1/user/{user_id}')
        return self._validate_and_convert(data, UserFullOutput)


class AsyncUsersResource(AsyncBaseResource):
    """Asynchronous user management operations."""

    def __init__(self, client: SnailOrbitAsyncClient) -> None:
        """Initialize async users resource."""
        super().__init__(client)

    async def list(
        self, search: str | None = None, filter: str | None = None, **params: Any
    ) -> AsyncIterator[UserFullOutput]:
        """List all users.

        Args:
            search: Search query to filter users
            filter: Filter query using query language (e.g., "name___contains:john and is_active___eq:true")
            **params: Other query parameters

        Yields:
            UserFullOutput objects
        """
        if search:
            params['search'] = search
        if filter:
            params['filter'] = filter
        async for user in self._paginate('/api/v1/user/list', UserFullOutput, params):
            yield user

    async def get(self, user_id: str) -> UserFullOutput:
        """Get a specific user by ID.

        Args:
            user_id: User ID

        Returns:
            UserFullOutput object
        """
        data = await self._get(f'/api/v1/user/{user_id}')
        return self._validate_and_convert(data, UserFullOutput)
