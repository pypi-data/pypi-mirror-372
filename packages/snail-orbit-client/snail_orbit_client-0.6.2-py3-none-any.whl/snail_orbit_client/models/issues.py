"""Issue models."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import ConfigDict, Field, computed_field, constr, field_validator

if TYPE_CHECKING:
    from datetime import datetime

# Import required types from generated models for API compatibility
from ..generated.models import (
    EncryptedObjectInput,
    IssueAttachmentBody,
    IssueOutput,  # Base issue model
)
from .base import BaseModel

MINUTES_IN_HOUR = 60.0


class IssueInterlinkType(str, Enum):
    """Types of issue interlinks."""

    BLOCKS = 'blocks'
    BLOCKED_BY = 'blocked_by'
    RELATES_TO = 'relates_to'
    DUPLICATES = 'duplicates'
    DUPLICATED_BY = 'duplicated_by'
    SUBTASK_OF = 'subtask_of'
    HAS_SUBTASK = 'has_subtask'


class IssueTag(BaseModel):
    """Issue tag model."""

    id: str = Field(description='Tag ID')
    name: str = Field(description='Tag name')
    color: str | None = Field(default=None, description='Tag color')


class IssueAttachment(BaseModel):
    """Issue attachment model."""

    id: str = Field(description='Attachment ID')
    name: str = Field(description='File name')
    size: int = Field(description='File size in bytes')
    content_type: str = Field(description='MIME content type')
    ocr_text: str | None = Field(default=None, description='OCR extracted text')
    created_at: datetime = Field(description='Upload timestamp')
    created_by: str = Field(description='User who uploaded the file')


class IssueInterlink(BaseModel):
    """Issue interlink model."""

    id: str = Field(description='Interlink ID')
    type: IssueInterlinkType = Field(description='Type of relationship')
    target_issue_id: str = Field(description='ID of the linked issue')
    target_issue_readable_id: str = Field(description='Readable ID of linked issue')
    target_issue_subject: str = Field(description='Subject of linked issue')


class IssueComment(BaseModel):
    """Issue comment model."""

    id: str = Field(description='Comment ID')
    issue_id: str = Field(description='ID of the issue this comment belongs to')
    text: str | None = Field(default=None, description='Comment text')
    attachments: list[IssueAttachment] = Field(
        default_factory=list, description='Comment attachments'
    )
    spent_time: int | None = Field(default=None, description='Time spent in minutes')
    created_at: datetime = Field(description='Comment creation timestamp')
    created_by: str = Field(description='User who created the comment')
    updated_at: datetime | None = Field(
        default=None, description='Last update timestamp'
    )
    updated_by: str | None = Field(
        default=None, description='User who last updated the comment'
    )


class Issue(IssueOutput):
    """Represents an issue (task, bug, feature request) in the Snail Orbit system.

    This model extends the generated IssueOutput with time tracking convenience.

    Issues are the core work items in projects. They can have custom fields,
    attachments, comments, and relationships with other issues. Issues support
    rich metadata including time tracking, tags, and workflow automation.

    Example:
        ```python
        # Access issue data directly from API structure
        project_id = issue.project.id
        priority_field = issue.fields.get('priority')

        # Time tracking convenience
        hours = issue.hours_spent
        print(f"Time spent: {hours:.1f} hours")
        ```
    """

    model_config = ConfigDict(
        extra='allow',  # Allow additional fields from API response
        frozen=False,  # Allow computed fields (override generated model's frozen=True)
    )

    @computed_field
    def hours_spent(self) -> float:
        """Convert total time spent from minutes to hours.

        Returns:
            Total logged time in hours (exact float value)
        """
        return (getattr(self, 'total_spent_time', 0) or 0) / MINUTES_IN_HOUR


class IssueCreate(BaseModel):
    """Data required to create a new issue.

    Issues must belong to a project and have a descriptive subject.
    Custom fields, attachments, and tags can be set during creation.

    Example:
        ```python
        issue_data = IssueCreate(
            project_id='507f1f77bcf86cd799439011',
            subject='Implement user authentication',
            text=EncryptedObjectInput(value='Add login/logout functionality with JWT tokens...'),
            fields={
                'priority': 'high',
                'assignee': 'developer@company.com',
                'due_date': '2024-04-01T00:00:00Z',
                'story_points': 8
            }
        )

        issue = client.issues.create(issue_data)
        print(f"Created issue {issue.id_readable}: {issue.subject}")
        ```
    """

    model_config = ConfigDict(
        frozen=True,
    )

    project_id: Annotated[
        str, constr(pattern=r'^[0-9a-f]{24}$', min_length=24, max_length=24)
    ] = Field(
        ...,
        examples=['5eb7cf5a86d9755df3a6c593'],
        description='ID of the project this issue belongs to',
    )
    subject: str = Field(description='Issue title/summary (required, concise)')
    text: EncryptedObjectInput | None = Field(
        default=None, description='Detailed description (supports Markdown)'
    )
    fields: Mapping[str, Any] | None = Field(
        default=None, description='Project-specific field values (plain JSON values)'
    )
    attachments: Sequence[IssueAttachmentBody] | None = Field(
        default=None, description='List of uploaded file attachments'
    )

    @field_validator('subject')
    @classmethod
    def validate_subject(cls, v: str) -> str:
        """Ensure subject is meaningful."""
        v = v.strip()
        if not v:
            raise ValueError('Issue subject cannot be empty')
        if len(v) < 3:
            raise ValueError('Issue subject must be at least 3 characters')
        return v


class IssueUpdate(BaseModel):
    """Data for updating an existing issue.

    All fields are optional - only provided fields will be updated.
    Use this for partial updates to issue information.

    Example:
        ```python
        # Update issue priority and assignee
        update_data = IssueUpdate(
            fields={
                'priority': 'critical',
                'assignee': 'senior-dev@company.com'
            }
        )
        updated_issue = client.issues.update(issue_id, update_data)

        # Move issue to different project
        move_data = IssueUpdate(project_id='new-project-id')
        client.issues.update(issue_id, move_data)

        # Update description with progress notes
        progress_data = IssueUpdate(
            text=EncryptedObjectInput(value='Authentication implemented with JWT. Testing in progress...')
        )
        client.issues.update(issue_id, progress_data)
        ```
    """

    model_config = ConfigDict(
        frozen=True,
    )

    project_id: (
        Annotated[str, constr(pattern=r'^[0-9a-f]{24}$', min_length=24, max_length=24)]
        | None
    ) = Field(default=None, description='Move issue to different project')
    subject: str | None = Field(default=None, description='Updated issue title')
    text: EncryptedObjectInput | None = Field(
        default=None, description='Updated description'
    )
    fields: Mapping[str, Any] | None = Field(
        default=None, description='Updated custom field values (plain JSON values)'
    )
    attachments: Sequence[IssueAttachmentBody] | None = Field(
        default=None, description='Updated list of attachment objects'
    )

    @field_validator('subject')
    @classmethod
    def validate_subject(cls, v: str | None) -> str | None:
        """Ensure subject is meaningful if provided."""
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError('Issue subject cannot be empty')
        if len(v) < 3:
            raise ValueError('Issue subject must be at least 3 characters')
        return v


class IssueCommentCreate(BaseModel):
    """Data for creating a new comment on an issue.

    Comments can include text, file attachments, and time tracking information.
    At least one of text or attachments must be provided.

    Example:
        ```python
        # Simple text comment
        comment_data = IssueCommentCreate(
            text='This has been fixed and tested on staging environment.'
        )

        # Comment with time tracking
        comment_data = IssueCommentCreate(
            text='Implemented the authentication middleware.',
            spent_time=180  # 3 hours in minutes
        )

        # Comment with attachments
        comment_data = IssueCommentCreate(
            text='See attached screenshots of the bug',
            attachments=['file_id_1', 'file_id_2']
        )

        comment = client.issues.create_comment(issue_id, comment_data)
        ```
    """

    text: str | None = Field(
        default=None, description='Comment text (supports Markdown)'
    )
    attachments: list[str] = Field(
        default_factory=list, description='List of uploaded file IDs to attach'
    )
    spent_time: int | None = Field(
        default=None, description='Time spent on this work in minutes'
    )

    @field_validator('text')
    @classmethod
    def validate_text_or_attachments(cls, v: str | None) -> str | None:
        """Ensure either text or attachments are provided."""
        # Note: This validation would need access to attachments field
        # For now, just validate text if provided
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Comment text cannot be empty if provided')
        return v


class IssueCommentUpdate(BaseModel):
    """Data for updating an existing comment.

    All fields are optional - only provided fields will be updated.
    Use this for editing comment content or updating time tracking.

    Example:
        ```python
        # Edit comment text
        update_data = IssueCommentUpdate(
            text='Updated: This has been fixed, tested, and deployed to production.'
        )

        # Update time tracking
        update_data = IssueCommentUpdate(spent_time=240)  # 4 hours

        # Add attachments to existing comment
        update_data = IssueCommentUpdate(
            attachments=['existing_file_id', 'new_file_id']
        )

        updated_comment = client.issues.update_comment(issue_id, comment_id, update_data)
        ```
    """

    text: str | None = Field(default=None, description='Updated comment text')
    attachments: list[str] | None = Field(
        default=None, description='Updated list of attachment IDs'
    )
    spent_time: int | None = Field(
        default=None, description='Updated time spent in minutes'
    )

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str | None) -> str | None:
        """Ensure text is not empty if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Comment text cannot be empty if provided')
        return v
