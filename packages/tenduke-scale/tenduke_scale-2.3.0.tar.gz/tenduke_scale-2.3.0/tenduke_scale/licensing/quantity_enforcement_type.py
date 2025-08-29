"""Quantity enforcement type enumeration."""

from enum import Enum


class QuantityEnforcementType(Enum):
    """Quantity enforcement type enumeration."""

    ENFORCED = "ENFORCED", "License checkouts enforce license constraints."
    METERED = "METERED", "License checkouts record and meter usage."
