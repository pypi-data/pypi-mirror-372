"""License key model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from tenduke_core.base_model import Model


# pylint: disable=duplicate-code
@dataclass
class LicenseKey(Model):
    """License key model.

    Attributes:
        license_key: License key string representation for use in API calls.
        allowed_activations: Number of activation codes allowed for the license key.
        created: When the license key was created.
        id: Unique id for the license key.
        modified: When the license key was last modified.
    """

    license_key: str = field(init=True, metadata={"api_name": "licenseKey"})
    allowed_activations: Optional[int] = field(
        init=True, metadata={"api_name": "allowedActivations"}, default=None
    )
    created: Optional[datetime] = field(init=True, metadata={"transform": "datetime"}, default=None)
    id: Optional[UUID] = field(init=True, metadata={"transform": "uuid"}, default=None)
    modified: Optional[datetime] = field(
        init=True, metadata={"transform": "datetime"}, default=None
    )
