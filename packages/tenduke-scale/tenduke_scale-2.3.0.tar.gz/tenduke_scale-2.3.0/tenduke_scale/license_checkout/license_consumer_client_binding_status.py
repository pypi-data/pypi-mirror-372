"""Model for describe consumer client bindings response."""

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Optional

from tenduke_core.base_model import Model

from .license_consumption_client_binding import LicenseConsumptionClientBinding


# "disable=duplicate-code" applied as splitting the declaration of the model type
# up across files would obfuscate the content and behaviour of the model.
# Also see pylint issue #7920 (https://github.com/PyCQA/pylint/issues/7920).
# Once that has been implemented, this can probably be removed.
#
# pylint: disable=duplicate-code
@dataclass
class LicenseConsumerClientBindingStatus(Model):
    """Model for describe consumer client bindings response.

    Attributes:
        all_client_bindings_included:
            Indicates whether the analysis of a users license consumption found more than the
            maximum response size worth of client bindings. A value equal to false means the
            response size was capped and true means all current client bindings have been included
            in the response. The maximum client binding count included in the response is 5 per
            license.
        client_bindings:
            Licenses that are currently known to be associated with a license consuming user using
            a specific application on a specific device. Note: this list size is limited to a
            predefined size and provides only a view into a small set of the most recent client
            bindings. Capping can be inspected by checking the flag: allClientBindingsIncluded.
    """

    all_client_bindings_included: Optional[bool] = field(
        init=True, metadata={"api_name": "allClientBindingsIncluded"}, default=None
    )
    client_bindings: Optional[Sequence[LicenseConsumptionClientBinding]] = field(
        init=True,
        metadata={
            "api_name": "clientBindings",
            "transform": "listtype",
            "type": LicenseConsumptionClientBinding,
        },
        default=None,
    )
