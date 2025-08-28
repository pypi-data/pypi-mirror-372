"""Project management resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import Project
from ..models import ProjectListItemOutput as ProjectListItem
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from ..client import SnailOrbitAsyncClient, SnailOrbitClient


class ProjectsResource(BaseResource):
    """Synchronous project management operations."""

    def __init__(self, client: SnailOrbitClient) -> None:
        """Initialize projects resource."""
        super().__init__(client)

    def list(
        self, search: str | None = None, filter: str | None = None, **params: Any
    ) -> Iterator[ProjectListItem]:
        """List all projects.

        Args:
            search: Search query to filter projects
            filter: Filter query using query language (e.g., "name___contains:demo and is_active___eq:true")
            **params: Other query parameters

        Yields:
            ProjectListItem objects
        """
        if search:
            params['search'] = search
        if filter:
            params['filter'] = filter
        yield from self._paginate('/api/v1/project/list', ProjectListItem, params)

    def get(self, project_id: str) -> Project:
        """Get a specific project by ID.

        Args:
            project_id: Project ID

        Returns:
            Project object
        """
        data = self._get(f'/api/v1/project/{project_id}')
        return self._validate_and_convert(data, Project)


class AsyncProjectsResource(AsyncBaseResource):
    """Asynchronous project management operations."""

    def __init__(self, client: SnailOrbitAsyncClient) -> None:
        """Initialize async projects resource."""
        super().__init__(client)

    async def list(
        self, search: str | None = None, filter: str | None = None, **params: Any
    ) -> AsyncIterator[ProjectListItem]:
        """List all projects.

        Args:
            search: Search query to filter projects
            filter: Filter query using query language (e.g., "name___contains:demo and is_active___eq:true")
            **params: Other query parameters

        Yields:
            ProjectListItem objects
        """
        if search:
            params['search'] = search
        if filter:
            params['filter'] = filter
        async for project in self._paginate(
            '/api/v1/project/list', ProjectListItem, params
        ):
            yield project

    async def get(self, project_id: str) -> Project:
        """Get a specific project by ID.

        Args:
            project_id: Project ID

        Returns:
            Project object
        """
        data = await self._get(f'/api/v1/project/{project_id}')
        return self._validate_and_convert(data, Project)
