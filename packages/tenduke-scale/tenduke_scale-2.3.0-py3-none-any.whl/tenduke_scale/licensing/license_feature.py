"""License feature model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from tenduke_core.base_model import Model


@dataclass
class LicenseFeature(Model):
    """License feature model.

    Attributes:
        created: When was the feature created.
        feature: Name of the feature.
        id: Unique id of the feature.
        modified: When was the feature last modified.
    """

    created: Optional[datetime] = field(init=True, metadata={"transform": "datetime"}, default=None)
    feature: Optional[str] = None
    id: Optional[UUID] = field(init=True, metadata={"transform": "uuid"}, default=None)
    modified: Optional[datetime] = field(
        init=True, metadata={"transform": "datetime"}, default=None
    )
