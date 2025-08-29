"""Model for the result of a release license call."""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from tenduke_core.base_model import Model

from ..licensing.quantity_dimension import QuantityDimension

QD = QuantityDimension


# "disable=duplicate-code" applied as splitting the declaration of the model type
# up across files would obfuscate the content and behaviour of the model.
# Also see pylint issue #7920 (https://github.com/PyCQA/pylint/issues/7920).
# Once that has been implemented, this can probably be removed.
#
# pylint: disable=duplicate-code


# The number of attributes here shadows the upstream API. Breaking this up would
# add complexity and make tracking things against the API documentation (and any
# future changes in the API harder).
#
# pylint: disable=too-many-instance-attributes
@dataclass
class LicenseReleaseResult(Model):
    """Model for LicenseReleaseResult object.

    Attributes:
        error_code: Short identifier for error condition.
        error_description: Textual description of error condition.
        final_used_quantity: The final amount used since initial license checkout.
        license_consumer_id: The consumer of the license/
        product_name: Product name for which license checkout was for.
        quantity_dimension:
            Enum: "SEATS" "USE_COUNT" "USE_TIME" Quantity dimension, related units of measurement:
            seats and use count = unitless, use time = seconds.
        released: Was the license released?
        released_lease_id: Lease id that has been released.
        released_license_id: License id of the release checkout.
        remaining_quantity: Remaining amount available for the license.
    """

    error_code: Optional[str] = field(
        init=True,
        metadata={"api_name": "errorCode"},
        default=None,
    )
    error_description: Optional[str] = field(
        init=True,
        metadata={"api_name": "errorDescription"},
        default=None,
    )
    final_used_quantity: Optional[int] = field(
        init=True,
        metadata={"api_name": "finalUsedQty"},
        default=None,
    )
    license_consumer_id: Optional[UUID] = field(
        init=True,
        metadata={"api_name": "licenseConsumerId", "transform": "uuid"},
        default=None,
    )
    product_name: Optional[str] = field(
        init=True,
        metadata={"api_name": "productName"},
        default=None,
    )
    quantity_dimension: Optional[QD] = field(
        init=True,
        metadata={
            "api_name": "qtyDimension",
            "transform": "enum",
            "type": QuantityDimension,
        },
        default=None,
    )
    released: Optional[bool] = None
    released_lease_id: Optional[str] = field(
        init=True,
        metadata={"api_name": "releasedLeaseId"},
        default=None,
    )
    released_license_id: Optional[UUID] = field(
        init=True,
        metadata={"api_name": "releasedLicenseId", "transform": "uuid"},
        default=None,
    )
    remaining_quantity: Optional[int] = field(
        init=True,
        metadata={"api_name": "remainingQty"},
        default=None,
    )
