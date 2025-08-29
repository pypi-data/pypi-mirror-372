"""Model for License model object."""

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
class LicenseModel(Model):
    """Model for License model object.

    Attributes:
        name: Name of the license model.
        concurrent_user_app_instances_per_seat:
            Defines maximum concurrent application instances per user per seat. Becomes effective
            if value is > 0. Application instance maps usually to an operating system process.
            NOTE: requires cliProcessId claim to be sent by client application checking out a
            license.
        concurrent_user_devices_per_seat:
            Defines maximum concurrent devices per user per seat. Becomes effective if value is > 0
            . Device instance maps usually to a work station, laptop, mobile device or similar.
            NOTE: requires cliHwId claim to be sent by client application when checking out a
            license.
        created: When the license model was created.
        id: Unique id of the license model.
        max_assignments_per_user:
            Defines maximum number of license consumptions (assignments) that a user can have per
            license.
        modified: When the license model was last modified.
    """

    name: str
    concurrent_user_app_instances_per_seat: Optional[int] = field(
        init=True,
        metadata={"api_name": "concurrentUserAppInstancesPerSeat"},
        default=None,
    )
    concurrent_user_devices_per_seat: Optional[int] = field(
        init=True, metadata={"api_name": "concurrentUserDevicesPerSeat"}, default=None
    )
    created: Optional[datetime] = field(init=True, metadata={"transform": "datetime"}, default=None)
    id: Optional[UUID] = field(init=True, metadata={"transform": "uuid"}, default=None)
    max_assignments_per_user: Optional[int] = field(
        init=True, metadata={"api_name": "maxAssignmentsPerUser"}, default=None
    )
    modified: Optional[datetime] = field(
        init=True, metadata={"transform": "datetime"}, default=None
    )
