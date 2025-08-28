"""Issue management resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import IssueCommentOutput
from ..models.issues import (
    Issue,
    IssueCommentCreate,
    IssueCommentUpdate,
    IssueCreate,
    IssueUpdate,
)
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from ..client import SnailOrbitAsyncClient, SnailOrbitClient


class IssuesResource(BaseResource):
    """Synchronous issue management operations."""

    def __init__(self, client: SnailOrbitClient) -> None:
        """Initialize issues resource."""
        super().__init__(client)

    def list(
        self, q: str | None = None, search: str | None = None, **params: Any
    ) -> Iterator[Issue]:
        """List issues with optional query.

        Args:
            q: Issue query language filter (e.g., "priority:high status:open")
            search: Text search query
            **params: Additional query parameters

        Yields:
            Issue objects
        """
        if q:
            params['q'] = q
        if search:
            params['search'] = search
        yield from self._paginate('/api/v1/issue/list', Issue, params)

    def get(self, issue_id: str) -> Issue:
        """Get a specific issue by ID.

        Args:
            issue_id: Issue ID

        Returns:
            Issue object
        """
        data = self._get(f'/api/v1/issue/{issue_id}')
        return self._validate_and_convert(data, Issue)

    def get_by_readable_id(self, readable_id: str) -> Issue:
        """Get an issue by its readable ID (e.g., PRJ-123).

        Args:
            readable_id: Human-readable issue ID

        Returns:
            Issue object
        """
        data = self._get(f'/api/v1/issue/{readable_id}')
        return self._validate_and_convert(data, Issue)

    def create(self, issue_data: IssueCreate | dict[str, Any]) -> Issue:
        """Create a new issue.

        Args:
            issue_data: Issue creation data

        Returns:
            Created issue object
        """
        if isinstance(issue_data, IssueCreate):
            data = issue_data.model_dump(exclude_unset=True)
        else:
            data = issue_data

        response = self._post('/api/v1/issue/', data)
        return self._validate_and_convert(response, Issue)

    def update(self, issue_id: str, issue_data: IssueUpdate | dict[str, Any]) -> Issue:
        """Update an existing issue.

        Args:
            issue_id: Issue ID
            issue_data: Issue update data

        Returns:
            Updated issue object
        """
        if isinstance(issue_data, IssueUpdate):
            data = issue_data.model_dump(exclude_unset=True)
        else:
            data = issue_data

        response = self._put(f'/api/v1/issue/{issue_id}', data)
        return self._validate_and_convert(response, Issue)

    def delete(self, issue_id: str) -> None:
        """Delete an issue.

        Args:
            issue_id: Issue ID
        """
        self._delete(f'/api/v1/issue/{issue_id}')

    def subscribe(self, issue_id: str) -> None:
        """Subscribe to issue notifications.

        Args:
            issue_id: Issue ID
        """
        self._post(f'/api/v1/issue/{issue_id}/subscribe')

    def unsubscribe(self, issue_id: str) -> None:
        """Unsubscribe from issue notifications.

        Args:
            issue_id: Issue ID
        """
        self._post(f'/api/v1/issue/{issue_id}/unsubscribe')

    # Comment operations
    def get_comments(self, issue_id: str) -> Iterator[IssueCommentOutput]:
        """Get comments for an issue.

        Args:
            issue_id: Issue ID

        Yields:
            Issue comment objects
        """
        yield from self._paginate(
            f'/api/v1/issue/{issue_id}/comment/list', IssueCommentOutput
        )

    def get_comment(self, issue_id: str, comment_id: str) -> IssueCommentOutput:
        """Get a specific comment.

        Args:
            issue_id: Issue ID
            comment_id: Comment ID

        Returns:
            Issue comment object
        """
        data = self._get(f'/api/v1/issue/{issue_id}/comment/{comment_id}')
        return self._validate_and_convert(data, IssueCommentOutput)

    def create_comment(
        self, issue_id: str, comment_data: IssueCommentCreate | dict[str, Any]
    ) -> IssueCommentOutput:
        """Create a new comment on an issue.

        Args:
            issue_id: Issue ID
            comment_data: Comment creation data

        Returns:
            Created comment object
        """
        if isinstance(comment_data, IssueCommentCreate):
            data = comment_data.model_dump(exclude_unset=True)
        else:
            data = comment_data

        response = self._post(f'/api/v1/issue/{issue_id}/comment', data)
        return self._validate_and_convert(response, IssueCommentOutput)

    def update_comment(
        self,
        issue_id: str,
        comment_id: str,
        comment_data: IssueCommentUpdate | dict[str, Any],
    ) -> IssueCommentOutput:
        """Update an existing comment.

        Args:
            issue_id: Issue ID
            comment_id: Comment ID
            comment_data: Comment update data

        Returns:
            Updated comment object
        """
        if isinstance(comment_data, IssueCommentUpdate):
            data = comment_data.model_dump(exclude_unset=True)
        else:
            data = comment_data

        response = self._put(f'/api/v1/issue/{issue_id}/comment/{comment_id}', data)
        return self._validate_and_convert(response, IssueCommentOutput)

    def delete_comment(self, issue_id: str, comment_id: str) -> None:
        """Delete a comment.

        Args:
            issue_id: Issue ID
            comment_id: Comment ID
        """
        self._delete(f'/api/v1/issue/{issue_id}/comment/{comment_id}')

    # Tag operations
    def add_tag(self, issue_id: str, tag_id: str) -> Issue:
        """Add a tag to an issue.

        Args:
            issue_id: Issue ID
            tag_id: Tag ID

        Returns:
            Updated issue object
        """
        data = self._post(f'/api/v1/issue/{issue_id}/tag', {'tag_id': tag_id})
        return self._validate_and_convert(data, Issue)

    def remove_tag(self, issue_id: str, tag_id: str) -> Issue:
        """Remove a tag from an issue.

        Args:
            issue_id: Issue ID
            tag_id: Tag ID

        Returns:
            Updated issue object
        """
        data = self._post(f'/api/v1/issue/{issue_id}/untag', {'tag_id': tag_id})
        return self._validate_and_convert(data, Issue)


class AsyncIssuesResource(AsyncBaseResource):
    """Asynchronous issue management operations."""

    def __init__(self, client: SnailOrbitAsyncClient) -> None:
        """Initialize async issues resource."""
        super().__init__(client)

    async def list(
        self, q: str | None = None, search: str | None = None, **params: Any
    ) -> AsyncIterator[Issue]:
        """List issues with optional query.

        Args:
            q: Issue query language filter (e.g., "priority:high status:open")
            search: Text search query
            **params: Additional query parameters

        Yields:
            Issue objects
        """
        if q:
            params['q'] = q
        if search:
            params['search'] = search
        async for issue in self._paginate('/api/v1/issue/list', Issue, params):
            yield issue

    async def get(self, issue_id: str) -> Issue:
        """Get a specific issue by ID.

        Args:
            issue_id: Issue ID

        Returns:
            Issue object
        """
        data = await self._get(f'/api/v1/issue/{issue_id}')
        return self._validate_and_convert(data, Issue)

    async def get_by_readable_id(self, readable_id: str) -> Issue:
        """Get an issue by its readable ID (e.g., PRJ-123).

        Args:
            readable_id: Human-readable issue ID

        Returns:
            Issue object
        """
        data = await self._get(f'/api/v1/issue/{readable_id}')
        return self._validate_and_convert(data, Issue)

    async def create(self, issue_data: IssueCreate | dict[str, Any]) -> Issue:
        """Create a new issue.

        Args:
            issue_data: Issue creation data

        Returns:
            Created issue object
        """
        if isinstance(issue_data, IssueCreate):
            data = issue_data.model_dump(exclude_unset=True)
        else:
            data = issue_data

        response = await self._post('/api/v1/issue/', data)
        return self._validate_and_convert(response, Issue)

    async def update(
        self, issue_id: str, issue_data: IssueUpdate | dict[str, Any]
    ) -> Issue:
        """Update an existing issue.

        Args:
            issue_id: Issue ID
            issue_data: Issue update data

        Returns:
            Updated issue object
        """
        if isinstance(issue_data, IssueUpdate):
            data = issue_data.model_dump(exclude_unset=True)
        else:
            data = issue_data

        response = await self._put(f'/api/v1/issue/{issue_id}', data)
        return self._validate_and_convert(response, Issue)

    async def delete(self, issue_id: str) -> None:
        """Delete an issue.

        Args:
            issue_id: Issue ID
        """
        await self._delete(f'/api/v1/issue/{issue_id}')

    async def subscribe(self, issue_id: str) -> None:
        """Subscribe to issue notifications.

        Args:
            issue_id: Issue ID
        """
        await self._post(f'/api/v1/issue/{issue_id}/subscribe')

    async def unsubscribe(self, issue_id: str) -> None:
        """Unsubscribe from issue notifications.

        Args:
            issue_id: Issue ID
        """
        await self._post(f'/api/v1/issue/{issue_id}/unsubscribe')

    # Comment operations
    async def get_comments(self, issue_id: str) -> AsyncIterator[IssueCommentOutput]:
        """Get comments for an issue.

        Args:
            issue_id: Issue ID

        Yields:
            Issue comment objects
        """
        async for comment in self._paginate(
            f'/api/v1/issue/{issue_id}/comment/list', IssueCommentOutput
        ):
            yield comment

    async def get_comment(self, issue_id: str, comment_id: str) -> IssueCommentOutput:
        """Get a specific comment.

        Args:
            issue_id: Issue ID
            comment_id: Comment ID

        Returns:
            Issue comment object
        """
        data = await self._get(f'/api/v1/issue/{issue_id}/comment/{comment_id}')
        return self._validate_and_convert(data, IssueCommentOutput)

    async def create_comment(
        self, issue_id: str, comment_data: IssueCommentCreate | dict[str, Any]
    ) -> IssueCommentOutput:
        """Create a new comment on an issue.

        Args:
            issue_id: Issue ID
            comment_data: Comment creation data

        Returns:
            Created comment object
        """
        if isinstance(comment_data, IssueCommentCreate):
            data = comment_data.model_dump(exclude_unset=True)
        else:
            data = comment_data

        response = await self._post(f'/api/v1/issue/{issue_id}/comment', data)
        return self._validate_and_convert(response, IssueCommentOutput)

    async def update_comment(
        self,
        issue_id: str,
        comment_id: str,
        comment_data: IssueCommentUpdate | dict[str, Any],
    ) -> IssueCommentOutput:
        """Update an existing comment.

        Args:
            issue_id: Issue ID
            comment_id: Comment ID
            comment_data: Comment update data

        Returns:
            Updated comment object
        """
        if isinstance(comment_data, IssueCommentUpdate):
            data = comment_data.model_dump(exclude_unset=True)
        else:
            data = comment_data

        response = await self._put(
            f'/api/v1/issue/{issue_id}/comment/{comment_id}', data
        )
        return self._validate_and_convert(response, IssueCommentOutput)

    async def delete_comment(self, issue_id: str, comment_id: str) -> None:
        """Delete a comment.

        Args:
            issue_id: Issue ID
            comment_id: Comment ID
        """
        await self._delete(f'/api/v1/issue/{issue_id}/comment/{comment_id}')

    # Tag operations
    async def add_tag(self, issue_id: str, tag_id: str) -> Issue:
        """Add a tag to an issue.

        Args:
            issue_id: Issue ID
            tag_id: Tag ID

        Returns:
            Updated issue object
        """
        data = await self._post(f'/api/v1/issue/{issue_id}/tag', {'tag_id': tag_id})
        return self._validate_and_convert(data, Issue)

    async def remove_tag(self, issue_id: str, tag_id: str) -> Issue:
        """Remove a tag from an issue.

        Args:
            issue_id: Issue ID
            tag_id: Tag ID

        Returns:
            Updated issue object
        """
        data = await self._post(f'/api/v1/issue/{issue_id}/untag', {'tag_id': tag_id})
        return self._validate_and_convert(data, Issue)
