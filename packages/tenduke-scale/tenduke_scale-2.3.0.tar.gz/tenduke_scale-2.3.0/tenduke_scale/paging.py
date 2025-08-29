"""Paging args for API calls."""

from dataclasses import dataclass, field
from typing import Optional

from tenduke_core.base_model import Model


@dataclass
class PagingOptions(Model):
    """Paging args for API calls.

    Any fields that are not `None` are added as headers to the API call.

    Attributes:
        offset:
            Offset for paging results. Defaults to 0. Applies to licenses, not the additional
            information included when parameter withMetadata == true.
        limit:
            Limit for controlling result size. Defaults to 5. Applies to licenses, not the
            additional information included when parameter withMetadata == true.
        order_by:
            Field name to order results by. Valid fields depend on object tyoe returned by
            call.
        order_asc:
            Flag that controls ordering in ascending vs. descending order. Defaults to false,
            meaning descending order.
    """

    offset: Optional[int] = field(init=True, metadata={"transform": "str"}, default=None)
    limit: Optional[int] = field(init=True, metadata={"transform": "str"}, default=None)
    order_by: Optional[str] = field(
        init=True, metadata={"api_name": "order-by", "transform": "str"}, default=None
    )
    order_asc: Optional[bool] = field(
        init=True, metadata={"api_name": "order-asc", "transform": "str"}, default=None
    )
