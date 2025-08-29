"""License metadata model."""

from dataclasses import dataclass, field
from typing import Optional

from tenduke_core.base_model import Model

from .effective_product_config_info import EffectiveProductConfigInfo
from .license_container import LicenseContainer
from .license_model import LicenseModel


@dataclass
class LicenseMetadata(Model):
    """License metadata model.

    Attributes:
        contract_reference:
            Optional reference field that associates a license with an external contract id. This
            field is present and has a value if it was included in the request when issuing the
            license.
        license_container: The license container that the license(s) are contained by.
        license_model: The license model that was assigned to the license(s) on creation.
        order_reference:
            Optional reference field that associates a license with an external order id. This
            field is present and has a value if it was included in the request when issuing the
            license.
        product_config_info:
            Optional product configuration information that was used as specification to issue the
            new licenses. This object is null or missing if issuing licenses was done by dynamic
            product name and features.
        product_reference:
            Optional reference field that associates a license with an external product id. This
            field is present and has a value if it was included in the request when issuing the
            license.
        subscription_reference:
            Optional reference field that associates a license with an external subscription id.
            This field is present and has a value if it was included in the request when issuing
            the license.
    """

    contract_reference: Optional[str] = field(
        init=True, metadata={"api_name": "contractReference"}, default=None
    )
    license_container: Optional[LicenseContainer] = field(
        init=True,
        metadata={
            "api_name": "licenseContainer",
            "transform": "type",
            "type": LicenseContainer,
        },
        default=None,
    )
    license_model: Optional[LicenseModel] = field(
        init=True,
        metadata={
            "api_name": "licenseModel",
            "transform": "type",
            "type": LicenseModel,
        },
        default=None,
    )
    order_reference: Optional[str] = field(
        init=True, metadata={"api_name": "orderReference"}, default=None
    )
    product_config_info: Optional[EffectiveProductConfigInfo] = field(
        init=True,
        metadata={
            "api_name": "productConfigInfo",
            "transform": "type",
            "type": EffectiveProductConfigInfo,
        },
        default=None,
    )
    product_reference: Optional[str] = field(
        init=True, metadata={"api_name": "productReference"}, default=None
    )
    subscription_reference: Optional[str] = field(
        init=True, metadata={"api_name": "subscriptionReference"}, default=None
    )
