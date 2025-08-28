"""Custom fields management resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import CustomField, CustomFieldGroup
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from ..client import SnailOrbitAsyncClient, SnailOrbitClient


class CustomFieldsResource(BaseResource):
    """Synchronous custom fields management operations."""

    def __init__(self, client: SnailOrbitClient) -> None:
        """Initialize custom fields resource."""
        super().__init__(client)

    # Custom Field Group operations
    def list_groups(self, **params: Any) -> Iterator[CustomFieldGroup]:
        """List custom field groups.

        Args:
            **params: Additional query parameters (search, filter, etc.)

        Yields:
            Custom field group objects
        """
        yield from self._paginate(
            '/api/v1/custom_field/group/list', CustomFieldGroup, params
        )

    def get_group(self, group_id: str) -> CustomFieldGroup:
        """Get a specific custom field group.

        Args:
            group_id: Group ID

        Returns:
            Custom field group object
        """
        data = self._get(f'/api/v1/custom_field/group/{group_id}')
        return self._validate_and_convert(data, CustomFieldGroup)

    # Custom Field operations (individual field access only)

    def get_field(self, field_id: str) -> CustomField:
        """Get a specific custom field.

        Args:
            field_id: Field ID

        Returns:
            Custom field object
        """
        data = self._get(f'/api/v1/custom_field/{field_id}')
        return self._validate_and_convert(data, CustomField)


class AsyncCustomFieldsResource(AsyncBaseResource):
    """Asynchronous custom fields management operations."""

    def __init__(self, client: SnailOrbitAsyncClient) -> None:
        """Initialize async custom fields resource."""
        super().__init__(client)

    # Custom Field Group operations
    async def list_groups(self, **params: Any) -> AsyncIterator[CustomFieldGroup]:
        """List custom field groups.

        Args:
            **params: Additional query parameters (search, filter, etc.)

        Yields:
            Custom field group objects
        """
        async for group in self._paginate(
            '/api/v1/custom_field/group/list', CustomFieldGroup, params
        ):
            yield group

    async def get_group(self, group_id: str) -> CustomFieldGroup:
        """Get a specific custom field group.

        Args:
            group_id: Group ID

        Returns:
            Custom field group object
        """
        data = await self._get(f'/api/v1/custom_field/group/{group_id}')
        return self._validate_and_convert(data, CustomFieldGroup)

    # Custom Field operations (individual field access only)

    async def get_field(self, field_id: str) -> CustomField:
        """Get a specific custom field.

        Args:
            field_id: Field ID

        Returns:
            Custom field object
        """
        data = await self._get(f'/api/v1/custom_field/{field_id}')
        return self._validate_and_convert(data, CustomField)
