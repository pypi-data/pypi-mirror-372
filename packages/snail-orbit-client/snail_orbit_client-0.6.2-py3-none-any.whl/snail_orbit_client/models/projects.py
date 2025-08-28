"""Project models."""

# Re-export generated models - manual models were redundant
from ..generated.models import ProjectAvatarType, ProjectListItemOutput
from ..generated.models import ProjectOutput as Project

__all__ = [
    'Project',
    'ProjectListItemOutput',
    'ProjectAvatarType',
]
