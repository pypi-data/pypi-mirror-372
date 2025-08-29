"""Consumer type enumeration."""

from enum import Enum


class ConsumerType(Enum):
    """Consumer type enumeration.

    Used to indicate if this is an individual or not. All types except PERSON behave in the same
    way in the API.
    """

    COMPANY = "COMPANY", "The license consumer is a company."
    ORGANIZATION = "ORGANIZATION", "The license consumer is an organization."
    PERSON = "PERSON", "The license consumer is a person."
    UNDEFINED = "UNDEFINED", "The type of the license consumer is not known."
