"""Custom field output models."""

# Import output models from generated for API compatibility
from ..generated.models import CustomFieldGroupOutput as CustomFieldGroup
from ..generated.models import CustomFieldOutput as CustomField

__all__ = ['CustomField', 'CustomFieldGroup']
