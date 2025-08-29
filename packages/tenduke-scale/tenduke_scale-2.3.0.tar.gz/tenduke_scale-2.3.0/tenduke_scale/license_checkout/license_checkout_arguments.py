"""Model for checking out enforced licenses or starting metered licenses."""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from tenduke_core.base_model import Model

from ..licensing.quantity_dimension import QuantityDimension

QD = QuantityDimension


@dataclass
class LicenseCheckoutArguments(Model):
    """Model for checking out enforced licenses or starting metered licenses.

    Attributes:
        product_name: Product name for which license checkout is requested.
        quantity_dimension:
            Enum: "SEATS" "USE_COUNT" "USE_TIME" Quantity dimension, related units of measurement:
            seats and use count = unitless, use time = seconds.
        quantity:
            Quantity defines how much to consume. NOTE: does not apply for seat based licensing.
            When using seats quantity is always equals to 1 (maximum qty = 1 when requesting to
            consume a seat, qtyDimension = SEATS).
        client_version:
            Client application version. NOTE: required when consuming licenses that have an allowed
            version range specified. Recommendation: client applications are encouraged to always
            send their version.
        license_id:
            Optional id of a specific license to consume. No license selection fallback logic kicks
            in if this value is defined. This means consumption either succeeds based on the
            specific license or fails with no further reason. Using this field is redunant if a
            license key is used.
    """

    product_name: str = field(init=True, metadata={"api_name": "productName"})
    quantity_dimension: QD = field(
        init=True,
        metadata={
            "api_name": "qtyDimension",
            "transform": "enum",
            "type": QuantityDimension,
        },
        default=QD.SEATS,
    )
    quantity: int = field(init=True, metadata={"api_name": "qty"}, default=1)
    client_version: Optional[str] = field(
        init=True, metadata={"api_name": "clientVersion"}, default=None
    )
    license_id: Optional[UUID] = field(
        init=True, metadata={"api_name": "licenseId", "transform": "uuid"}, default=None
    )
