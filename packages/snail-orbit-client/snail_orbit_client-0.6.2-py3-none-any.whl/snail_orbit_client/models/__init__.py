"""Pydantic models for Snail Orbit API objects."""

from ..generated.models import (
    EncryptedObjectInput,
    IssueAttachmentBody,
    IssueCommentOutput,
)
from .activity import Activity
from .auth import Profile, User, UserFullOutput
from .base import BaseModel, PaginatedResponse
from .custom_fields import CustomField, CustomFieldGroup

# Manual models with convenience methods
from .issues import (
    Issue,
    IssueComment,
    IssueCommentCreate,
    IssueCommentUpdate,
    IssueCreate,
    IssueUpdate,
)
from .projects import Project, ProjectListItemOutput

__all__ = [
    # Base
    'BaseModel',
    'PaginatedResponse',
    # Activity
    'Activity',
    # Authentication & Users
    'User',
    'UserFullOutput',
    'Profile',
    # Custom Fields
    'CustomField',
    'CustomFieldGroup',
    # Issues
    'Issue',
    'IssueComment',
    'IssueCommentCreate',
    'IssueCommentOutput',
    'IssueCommentUpdate',
    'IssueCreate',
    'IssueUpdate',
    # Projects
    'Project',
    'ProjectListItemOutput',
    # Field types (from generated - used in manual models)
    'EncryptedObjectInput',
    'IssueAttachmentBody',
]
