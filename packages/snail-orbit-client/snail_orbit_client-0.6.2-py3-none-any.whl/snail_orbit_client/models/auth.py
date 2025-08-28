"""Authentication and user models."""

# Re-export generated models - manual models were redundant duplicates
from ..generated.models import Profile, UserAvatarType, UserFullOutput, UserOriginType
from ..generated.models import UserOutput as User

__all__ = [
    'User',
    'UserFullOutput',
    'Profile',
    'UserAvatarType',
    'UserOriginType',
]
