"""Model for arguments to describe license operations."""

from dataclasses import dataclass, field
from typing import Optional

from tenduke_core.base_model import Model


@dataclass
class DescribeLicenseOptions(Model):
    """Model for arguments to describe license operations.

    Attributes:
        filter_field:
            Name of field to apply filter value on. Valid fields depend on object tyoe returned by
            call.
        filter_value: Filter value to apply on licenses.
        with_metadata:
            Flag to control including verbose information about the licenses and client bindings.
            Setting this option to true will fetch contract, order, subscription and external
            reference information at time of original license grant, the license container, a
            possible license key and related product information. For client bindings the
            additional information is related to license consumption objects and license consumers.
            Defaults to false.
    """

    filter_field: Optional[str] = field(
        init=True, metadata={"api_name": "filterField"}, default=None
    )
    filter_value: Optional[str] = field(
        init=True, metadata={"api_name": "filterValue"}, default=None
    )
    with_metadata: Optional[bool] = field(
        init=True,
        metadata={"api_name": "withMetadata", "transform": "str"},
        default=None,
    )

    def to_query_string(self) -> str:
        """Convert object to query string fragment.

        Returns:
            Attributes of object formatted for inclusion in the query string of an HTTP request to
            the API.
        """
        data = self.to_api()
        key_values = [f"{k}={v}" for k, v in data.items()]
        return "&".join(key_values)
