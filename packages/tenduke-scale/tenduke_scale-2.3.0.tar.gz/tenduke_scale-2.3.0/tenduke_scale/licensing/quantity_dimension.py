"""Quantity dimension enumeration."""

from enum import Enum


class QuantityDimension(Enum):
    """Quantity dimension enumeration."""

    SEATS = "SEATS", "Quantity in interpreted as number of seats."
    USE_COUNT = "USE_COUNT", "Quantity in interpreted as number of uses."
    USE_TIME = "USE_TIME", "Quantity in interpreted as amount of time used for."
