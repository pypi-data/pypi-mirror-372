"""Feature flags response fields."""

from collections.abc import Sequence
from dataclasses import dataclass, field

from tenduke_core.base_model import Model


@dataclass
class FeatureFlagsResponse(Model):
    """Feature flags for a product.

    Attributes:
        product_name: Name of the product.
        features: List of feature names.
    """

    product_name: str = field(init=True, metadata={"api_name": "productName"})
    features: Sequence[str] = field(init=True)
