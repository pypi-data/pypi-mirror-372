"""License container model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from tenduke_core.base_model import Model


# "disable=duplicate-code" applied as splitting the declaration of the model type
# up across files would obfuscate the content and behaviour of the model.
# Also see pylint issue #7920 (https://github.com/PyCQA/pylint/issues/7920).
# Once that has been implemented, this can probably be removed.
#
# pylint: disable=duplicate-code
@dataclass
class LicenseContainer(Model):
    """License container model.

    Attributes:
        created: When the license container was created.
        id: Unique id of the license container.
        modified: When the license container was last modified.
        name: Name to identify license container.
        used_as_default: Indicates if this is the default container for the licensee.
    """

    created: Optional[datetime] = field(init=True, metadata={"transform": "datetime"}, default=None)
    id: Optional[UUID] = field(init=True, metadata={"transform": "uuid"}, default=None)
    modified: Optional[datetime] = field(
        init=True, metadata={"transform": "datetime"}, default=None
    )
    name: Optional[str] = None
    used_as_default: Optional[bool] = field(
        init=True, metadata={"api_name": "usedAsDefault"}, default=None
    )
