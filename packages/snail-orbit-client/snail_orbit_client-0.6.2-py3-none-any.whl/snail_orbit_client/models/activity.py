"""Activity models."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

from pydantic import Field, field_validator

from ..generated.models import Activity as GeneratedActivity
from ..generated.models import IssueChangeOutput as GeneratedIssueChangeOutput


class IssueChangeOutput(GeneratedIssueChangeOutput):
    """Enhanced IssueChangeOutput that handles nested discriminated unions properly."""

    def __getattr__(self, name: str) -> Any:
        """Provide transparent access to root properties, handling nested discriminated unions."""
        # First check direct root properties (for subject/text changes)
        if hasattr(self.root, name):
            return getattr(self.root, name)

        # For nested discriminated unions (field changes), check the inner root
        if hasattr(self.root, 'root') and hasattr(self.root.root, name):
            return getattr(self.root.root, name)

        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def __setattr__(self, name: str, value: Any) -> None:
        """Provide transparent setting of root properties."""
        if name == 'root' or name.startswith('_'):
            super().__setattr__(name, value)
        elif hasattr(self.root, name):
            setattr(self.root, name, value)
        elif hasattr(self.root, 'root') and hasattr(self.root.root, name):
            setattr(self.root.root, name, value)
        else:
            super().__setattr__(name, value)


class Activity(GeneratedActivity):
    """Enhanced Activity model with proper enhanced wrapper usage."""

    # Override to use enhanced wrapper instead of RootModel
    changes: Sequence[IssueChangeOutput] | None = Field(default=None, title='Changes')

    @field_validator('changes', mode='before')
    @classmethod
    def convert_changes_to_enhanced_wrappers(cls, v: Any) -> Any:
        """Convert raw IssueChangeOutputRootModel to enhanced IssueChangeOutput wrappers."""
        if not v:
            return v

        enhanced_changes = []
        for change in v:
            if hasattr(change, 'root'):
                # Convert RootModel to enhanced wrapper
                enhanced_change = IssueChangeOutput(root=change.root)
                enhanced_changes.append(enhanced_change)
            elif isinstance(change, dict):
                # Raw API data
                enhanced_change = IssueChangeOutput.model_validate(change)
                enhanced_changes.append(enhanced_change)
            else:
                # Already an enhanced wrapper
                enhanced_changes.append(change)

        return enhanced_changes
