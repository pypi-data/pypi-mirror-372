"""Arguments for license heartbeat API operation."""

from dataclasses import dataclass, field

from tenduke_core.base_model import Model


@dataclass
class LicenseHeartbeatArguments(Model):
    """Arguments for license heartbeat API operation.

    Attributes:
        lease_id:
            Lease id value as it was returned in last heartbeat response or initial license
            checkout if no heartbeat has been done before this heartbeat request.
        treat_as_incremental_quantity:
            Default: False. Flag that tells if the usedQty value is absolute or should be treated
            as an increment. NOTE: does NOT APPLY when using SEAT based licensing.
        used_quantity:
            The amount used since initial license checkout / previous heartbeat. The usage quantity
            is an absolute value by default. Set field treatAsIncrementalQty = true to use an
            incremental tracking algorithm instead. NOTE: does NOT APPLY when using SEAT based
            licensing.
    """

    lease_id: str = field(init=True, metadata={"api_name": "leaseId"})
    treat_as_incremental_quantity: bool = field(
        init=True,
        metadata={"api_name": "treatAsIncrementalQty", "transform": "bool"},
        default=False,
    )
    used_quantity: int = field(init=True, metadata={"api_name": "usedQty"}, default=1)
