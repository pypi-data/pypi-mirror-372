"""Model for license object."""

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from tenduke_core.base_model import Model

from .license_feature import LicenseFeature
from .license_key import LicenseKey
from .license_metadata import LicenseMetadata
from .quantity_dimension import QuantityDimension
from .quantity_enforcement_type import QuantityEnforcementType

QD = QuantityDimension
QET = QuantityEnforcementType


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
class License(Model):
    """Model for license object.

    Attributes:
        product_name:
        quantity_dimension:
        quantity_enforcement_type:
        allowed_version_lower_bound:
            Lower bound of allowed client application version. A null and empty value is
            interpreted as version = undefined (any version allowed). Note: version identifiers are
            compared by their natural sort order to determine if one version is more or less than
            another being compared to.
        allowed_version_upper_bound:
            Upper bound of allowed client application version. A null and empty value is
            interpreted as version = undefined (any version allowed).
        concurrent_user_app_instances_per_seat:
            Defines maximum concurrent application instances per user per seat. Becomes effective
            if value is > 0. Application instance maps usually to an operating system process.
            NOTE: requires cliProcessId claim to be sent by client application checking out a
            license.
        created: When the license was created.
        display_name: License name in the format that can be used for presentation purposes.
        feature_names: List of feature names the license enables.
        features:
            List of features this license enables. Note that the feature list may be empty and a
            minimum viable license works on basis of a product name
        id: Unique id of the license.
        license_key:
            List of features this license enables. Note that the feature list may be empty and a
            minimum viable license works on basis of a product name.
        license_metadata:
            Information about the license and associations it has. This object is not present by
            default. To include metadata in a license read or list response the caller must ask for
            it.
        modified: When the license was last modified.
        quantity:
            The pure numerical part of quantity assigned to a license. Maximum qty = 1000 when
            qtyDimension = SEATS. Note: qty = -1 denotes metered use license and is not applicable
            for licenses that function in enforcing mode.
        valid_from: Defines date-time when license(s) validity starts.
        valid_until: Defines date-time when license(s) expires.
    """

    product_name: str = field(init=True, metadata={"api_name": "productName"})
    quantity_dimension: QD = field(
        init=True,
        metadata={
            "api_name": "qtyDimension",
            "transform": "enum",
            "type": QuantityDimension,
        },
    )
    quantity_enforcement_type: QET = field(
        init=True,
        metadata={
            "api_name": "qtyEnforcementType",
            "transform": "enum",
            "type": QuantityEnforcementType,
        },
    )
    allowed_version_lower_bound: Optional[str] = field(
        init=True, metadata={"api_name": "allowedVersionLowerBound"}, default=None
    )
    allowed_version_upper_bound: Optional[str] = field(
        init=True, metadata={"api_name": "allowedVersionUpperBound"}, default=None
    )
    allowed_versions_display_name: Optional[str] = field(
        init=True, metadata={"api_name": "allowedVersionsDisplayName"}, default=None
    )
    concurrent_user_app_instances_per_seat: Optional[int] = field(
        init=True,
        metadata={"api_name": "concurrentUserAppInstancesPerSeat"},
        default=None,
    )
    concurrent_user_devices_per_seat: Optional[int] = field(
        init=True, metadata={"api_name": "concurrentUserDevicesPerSeat"}, default=None
    )
    created: Optional[datetime] = field(init=True, metadata={"transform": "datetime"}, default=None)
    display_name: Optional[str] = field(
        init=True, metadata={"api_name": "displayName"}, default=None
    )
    feature_names: Optional[str] = field(
        init=True, metadata={"api_name": "featureNames"}, default=None
    )
    features: Optional[Sequence[LicenseFeature]] = field(
        init=True,
        metadata={"transform": "listtype", "type": LicenseFeature},
        default=None,
    )
    id: Optional[UUID] = field(init=True, metadata={"transform": "uuid"}, default=None)
    license_key: Optional[LicenseKey] = field(
        init=True,
        metadata={"api_name": "licenseKey", "transform": "type", "type": LicenseKey},
        default=None,
    )
    license_metadata: Optional[LicenseMetadata] = field(
        init=True,
        metadata={
            "api_name": "licenseMetadata",
            "transform": "type",
            "type": LicenseMetadata,
        },
        default=None,
    )
    modified: Optional[datetime] = field(
        init=True, metadata={"transform": "datetime"}, default=None
    )
    quantity: Optional[int] = field(init=True, metadata={"api_name": "qty"}, default=None)
    valid_from: Optional[datetime] = field(
        init=True,
        metadata={"api_name": "validFrom", "transform": "datetime"},
        default=None,
    )
    valid_until: Optional[datetime] = field(
        init=True,
        metadata={"api_name": "validUntil", "transform": "datetime"},
        default=None,
    )
