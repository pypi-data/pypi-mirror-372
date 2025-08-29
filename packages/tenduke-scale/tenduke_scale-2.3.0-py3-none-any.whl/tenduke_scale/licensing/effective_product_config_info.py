"""Model for product configuration information."""

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from tenduke_core.base_model import Model

from .quantity_dimension import QuantityDimension

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
class EffectiveProductConfigInfo(Model):
    """Model for product configuration information.

    Attributes:
        features: Formal names of the enabled features in the configuration.
        license_model_id: Unique id of the license model.
        license_model_name: Formal name of the license model.
        product_config_display_name: Display name of the product configuration.
        product_config_id: Unique id of the product configuration.
        product_config_name: Formal name of the product configuration.
        product_display_name: Display name of the product.
        product_id: Unique id of the product.
        product_name: Formal name of the product.
        quantity_dimension:
            Enum: "SEATS" "USE_COUNT" "USE_TIME". Dimension of the quantity that licenses granted
            based on the product configuration have. Units of measurement: seats and use count =
            unitless, use time = seconds.
        created: When the product configuration was created.
        id: Unique id of the product configuration.
        modified: When the product configuration was last modified.
    """

    features: Sequence[str]
    license_model_id: UUID = field(
        init=True, metadata={"api_name": "licenseModelId", "transform": "uuid"}
    )
    license_model_name: str = field(init=True, metadata={"api_name": "licenseModelName"})
    product_config_display_name: str = field(
        init=True, metadata={"api_name": "productConfigDisplayName"}
    )
    product_config_id: UUID = field(
        init=True, metadata={"api_name": "productConfigId", "transform": "uuid"}
    )
    product_config_name: str = field(init=True, metadata={"api_name": "productConfigName"})
    product_display_name: str = field(init=True, metadata={"api_name": "productDisplayName"})
    product_id: UUID = field(init=True, metadata={"api_name": "productId", "transform": "uuid"})
    product_name: str = field(init=True, metadata={"api_name": "productName"})
    quantity_dimension: QD = field(
        init=True,
        metadata={
            "api_name": "qtyDimension",
            "transform": "enum",
            "type": QuantityDimension,
        },
    )
    created: Optional[datetime] = field(init=True, metadata={"transform": "datetime"}, default=None)
    id: Optional[UUID] = field(init=True, metadata={"transform": "uuid"}, default=None)
    modified: Optional[datetime] = field(
        init=True, metadata={"transform": "datetime"}, default=None
    )
