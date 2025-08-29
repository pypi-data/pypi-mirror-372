"""License consumer data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from tenduke_core.base_model import Model

from .consumer_type import ConsumerType

CT = ConsumerType


# The number of attributes here shadows the upstream API. Breaking this up would
# add complexity and make tracking things against the API documentation (and any
# future changes in the API harder).
#
# pylint: disable=too-many-instance-attributes
@dataclass
class LicenseConsumer(Model):
    """Represents an entity that consumes and/or owns licenses.

    Attributes:
        name: Technical name which carries significance for finding and matching data.
        type: Enum: "DEVICE" "LICENSE_KEY" "PERSON".
        connected_identity_id:
            Optional identifier of an identity domain entity that this object maps to. The most
            common example is a user id, meaning the OIDC subject value in Id Tokens. The sub claim
            is used to match license consumer entities in licensing when using Id Token to
            authorize API calls. This id field may also denote a computer component or device
            (technical actor generally). In this case the license consumer type would also indicate
            a non human type.
        contact_info: Optional contact information data to store with identity type objects.
        created: When the consumer object was created.
        description: Optional description.
        display_label: Optional label intended to be used for presentation purposes.
        display_name: Optional name intended to be used for presentation purposes.
        email: Optional email address, value must be unique when specified.
        external_reference:
            Optional reference field that helps associate licensing data with data in other
            systems. NOTE: value must be unique per object (null allowed).
        id: Unique id for license consumer.
        modified: When the license consumer was last modified.
        natural_id:
            A unique natural id for the licensee. The value may be e.g. a customer account id,
            company VAT id, a user identifier or any unique value that makes sense in the system
            that owns customer master data records. If value is not provided it will be generated.
    """

    name: str
    type: CT = field(init=True, metadata={"transform": "enum", "type": ConsumerType})
    connected_identity_id: Optional[str] = field(
        init=True, metadata={"api_name": "connectedIdentityId"}, default=None
    )
    contact_info: Optional[str] = field(
        init=True, metadata={"api_name": "contactInfo"}, default=None
    )
    created: Optional[datetime] = field(init=True, metadata={"transform": "datetime"}, default=None)
    description: Optional[str] = None
    display_label: Optional[str] = field(
        init=True, metadata={"api_name": "displayLabel"}, default=None
    )
    display_name: Optional[str] = field(
        init=True, metadata={"api_name": "displayName"}, default=None
    )
    email: Optional[str] = None
    external_reference: Optional[str] = field(
        init=True, metadata={"api_name": "externalReference"}, default=None
    )
    id: Optional[UUID] = field(init=True, metadata={"transform": "uuid"}, default=None)
    modified: Optional[datetime] = field(
        init=True, metadata={"transform": "datetime"}, default=None
    )
    natural_id: Optional[str] = field(init=True, metadata={"api_name": "naturalId"}, default=None)
