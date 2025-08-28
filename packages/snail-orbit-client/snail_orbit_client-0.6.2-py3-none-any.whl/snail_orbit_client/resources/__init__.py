"""Resource managers for different API endpoints."""

from .auth import AsyncAuthResource, AuthResource
from .custom_fields import AsyncCustomFieldsResource, CustomFieldsResource
from .issues import AsyncIssuesResource, IssuesResource
from .projects import AsyncProjectsResource, ProjectsResource
from .users import AsyncUsersResource, UsersResource

__all__ = [
    'AuthResource',
    'AsyncAuthResource',
    'UsersResource',
    'AsyncUsersResource',
    'ProjectsResource',
    'AsyncProjectsResource',
    'IssuesResource',
    'AsyncIssuesResource',
    'CustomFieldsResource',
    'AsyncCustomFieldsResource',
]
