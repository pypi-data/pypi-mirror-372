"""Model for releasing enforced licenses or ending use of metered licenses."""

from dataclasses import dataclass, field
from typing import Optional

from tenduke_core.base_model import Model


@dataclass
class LicenseReleaseArguments(Model):
    """Model for releasing enforced licenses or ending use of metered licenses.

    Attributes:
        lease_id:
            Lease id value as it was returned in last heartbeat response or initial license
            checkout if no heartbeat has been done before release.
        final_quantity_used:
            The final amount used since initial license checkout. NOTE: does not apply when using
            seat based licensing.
    """

    lease_id: str = field(init=True, metadata={"api_name": "leaseId"})
    final_quantity_used: Optional[int] = field(
        init=True, metadata={"api_name": "finalUsedQty"}, default=None
    )
