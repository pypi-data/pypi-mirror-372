"""Authentication and profile resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Profile
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from ..client import SnailOrbitAsyncClient, SnailOrbitClient


class AuthResource(BaseResource):
    """Synchronous authentication and profile operations."""

    def __init__(self, client: SnailOrbitClient) -> None:
        """Initialize auth resource."""
        super().__init__(client)

    def get_profile(self) -> Profile:
        """Get current user profile.

        Returns:
            Current user profile information
        """
        data = self._get('/api/v1/profile')
        return self._validate_and_convert(data, Profile)


class AsyncAuthResource(AsyncBaseResource):
    """Asynchronous authentication and profile operations."""

    def __init__(self, client: SnailOrbitAsyncClient) -> None:
        """Initialize async auth resource."""
        super().__init__(client)

    async def get_profile(self) -> Profile:
        """Get current user profile.

        Returns:
            Current user profile information
        """
        data = await self._get('/api/v1/profile')
        return self._validate_and_convert(data, Profile)
