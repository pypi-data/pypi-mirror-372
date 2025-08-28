"""Base model classes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from datetime import datetime

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field


class BaseModel(PydanticBaseModel):
    """Base model for all Snail Orbit objects."""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=False,
        extra='forbid',
        str_strip_whitespace=True,
        validate_default=True,
    )


class AuditedModel(BaseModel):
    """Base model with audit fields for backward compatibility.

    Note: New models should inherit from generated models instead.
    """

    created_at: datetime = Field(description='When the object was created')
    updated_at: datetime | None = Field(
        default=None, description='When the object was last updated'
    )
    created_by: str = Field(description='ID of user who created this object')
    updated_by: str | None = Field(
        default=None, description='ID of user who last updated this object'
    )


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    count: int = Field(description='Total number of items')
    limit: int = Field(description='Maximum items per page')
    offset: int = Field(description='Number of items skipped')
    items: list[T] = Field(description='List of items in this page')

    @property
    def has_next(self) -> bool:
        """Check if there are more pages."""
        return self.offset + self.limit < self.count

    @property
    def has_previous(self) -> bool:
        """Check if there are previous pages."""
        return self.offset > 0

    @property
    def page_number(self) -> int:
        """Current page number (1-indexed)."""
        return (self.offset // self.limit) + 1

    @property
    def total_pages(self) -> int:
        """Total number of pages."""
        if self.limit == 0:
            return 1
        return (self.count + self.limit - 1) // self.limit
