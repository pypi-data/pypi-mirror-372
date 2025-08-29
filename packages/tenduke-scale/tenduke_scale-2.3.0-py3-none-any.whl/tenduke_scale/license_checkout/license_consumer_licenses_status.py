"""Model for describe consumer licenses response."""

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Optional

from tenduke_core.base_model import Model

from ..licensing.license import License


# "disable=duplicate-code" applied as splitting the declaration of the model type
# up across files would obfuscate the content and behaviour of the model.
# Also see pylint issue #7920 (https://github.com/PyCQA/pylint/issues/7920).
# Once that has been implemented, this can probably be removed.
#
# pylint: disable=duplicate-code
@dataclass
class LicenseConsumerLicensesStatus(Model):
    """Model for describe consumer licenses response.

    Attributes:
        licenses: Licenses that are accessible by the license consumer.
    """

    licenses: Optional[Sequence[License]] = field(
        init=True, metadata={"transform": "listtype", "type": License}, default=None
    )
