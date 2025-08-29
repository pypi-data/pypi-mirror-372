"""Model for providing client details to checkout operations."""

from dataclasses import dataclass, field
from typing import Optional

from tenduke_core.base_model import Model


# The number of attributes here shadows the upstream API. Breaking this up would
# add complexity and make tracking things against the API documentation (and any
# future changes in the API harder).
#
# pylint: disable=too-many-instance-attributes
@dataclass
class ClientDetails(Model):
    """Model for providing client details to checkout operations.

    Attributes:
        country: Country code of OS environment that the client app runs on.
        host_name: Hostname of device that the client app runs on.
        hardware_architecture: Architecture of of device / platform that the client app runs on.
        hardware_id:
            Hardware id of device that the client app runs on. This claim is required to implement
            concurrency rules over a user's devices.
        hardware_label: Hardware label of device that the client app runs on.
        installation_id: Installation id the client app.
        language: Language code of the OS environment that the client app runs on.
        process_id:
            Process id of client app process in OS environment that the client app runs on. This
            claim is required to implement concurrency rules over a user's application instances
            (processes).
        version:
            Client app version. This claim is required to implement rules about allowed versions
            and enforcing that a license is usable only for certain client application versions.
            The specified version is compared lexicographically to lower and upper bounds in
            available licenses. If a license id is used in checkout then the client version must be
            within the allowed version range in that specific license. Version is enforced only if
            the license requires it.
    """

    country: Optional[str] = field(init=True, metadata={"api_name": "cliCountry"}, default=None)
    host_name: Optional[str] = field(init=True, metadata={"api_name": "cliHostName"}, default=None)
    hardware_architecture: Optional[str] = field(
        init=True, metadata={"api_name": "cliHwArch"}, default=None
    )
    hardware_id: Optional[str] = field(init=True, metadata={"api_name": "cliHwId"}, default=None)
    hardware_label: Optional[str] = field(
        init=True, metadata={"api_name": "cliHwLabel"}, default=None
    )
    installation_id: Optional[str] = field(
        init=True, metadata={"api_name": "cliInstallationId"}, default=None
    )
    language: Optional[str] = field(init=True, metadata={"api_name": "cliLang"}, default=None)
    process_id: Optional[str] = field(
        init=True, metadata={"api_name": "cliProcessId"}, default=None
    )
    version: Optional[str] = field(init=True, metadata={"api_name": "cliVersion"}, default=None)
