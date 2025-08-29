"""Model for license consumption client binding object."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from tenduke_core.base_model import Model

from ..licensing.license import License
from ..licensing.license_consumer import LicenseConsumer


# pylint: disable=too-many-instance-attributes
@dataclass
class LicenseConsumptionClientBinding(Model):
    """Model for license consumption client binding object.

    Attributes:
        client_api_key: API key specified in client claims at checkout.
        client_country: Country code of OS environment that the client app runs on.
        client_host_name: Hostname of device that the client app runs on.
        client_hardware_architecture:
            Architecture of of device / platform that the client app runs on.
        client_hardware_id:
            Hardware id of device that the client app runs on. This claim is required to implement
            concurrency rules over a user's devices.
        client_hardware_label: Hardware label of device that the client app runs on.
        client_installation_id: Installation id the client app.
        client_language: Language code of the OS environment that the client app runs on.
        client_network_ip_address:
        client_os_user_name: User name from OS environment session client app is running in.
        client_os: Name of OS environment that the client app runs on.
        client_process_id:
            Process id of client app process in OS environment that the client app runs on. This
            claim is required to implement concurrency rules over a user's application instances
            (processes).
        client_version:
            Client app version. This claim is required to implement rules about allowed versions
            and enforcing that a license is usable only for certain client application versions.
            The specified version is compared lexicographically to lower and upper bounds in
            available licenses. If a license id is used in checkout then the client version must be
            within the allowed version range in that specific license. Version is enforced only if
            the license requires it.
        consume_duration_ended_at: When the consumption ended.
        consume_duration_granted_at: When the consumption was granted.
        created: When the client binding was created.
        id: Unique identifier for the client binding.
        last_heartbeat: When the last successful heartbeat was received.
        lease_id: Lease id of the lease associated with this binding.
        license: The license that this binding is associated with.
        license_consumer: The consumer of the license binding.
        locked: Indicates whether the consumption is locked to this hardware.
        modified: When the client binding was last modified.
        quantity_pre_allocated:
            Consumption amount allocated at checkout.
            Pre-allocating a quantity amount applies to quantity types that pure deductible nature,
            e.g. use count and use time. Its an indicative amount of e.g. use count or use time
            that a client estimates it needs to complete a task (may be end user driven). Client
            applications may use pre-allocation to ensure a certain amount of quantity is still
            available when starting a task. The pre-allocation is deducted from the available
            quantity and the final outcome is computed at time of release. The verified quantity is
            set at time of release and if the factual used quantity is less than what pass
            pre-allocated then the difference is refunded. NOTE: does not apply when consuming
            seats.
        request_ip_address: Address requesting the client binding.
        triggered_seat_use: Indicates if this client binding used a new seat.
        valid_from: Start of binding validity period.
        valid_until: End of binding validity period.
        verified_quantity:
            Verified quantity is determined by the consuming client informing the licensing API of
            factual use. This can happen at time of heartbeat and release. The verified quantity is
            applies to quantity types that pure deductible nature, e.g. use count and use time.
            NOTE: does not apply when consuming seats.
    """

    client_api_key: Optional[str] = field(
        init=True, metadata={"api_name": "cliApiKey"}, default=None
    )
    client_country: Optional[str] = field(
        init=True, metadata={"api_name": "cliCountry"}, default=None
    )
    client_host_name: Optional[str] = field(
        init=True, metadata={"api_name": "cliHostName"}, default=None
    )
    client_hardware_architecture: Optional[str] = field(
        init=True, metadata={"api_name": "cliHwArch"}, default=None
    )
    client_hardware_id: Optional[str] = field(
        init=True, metadata={"api_name": "cliHwId"}, default=None
    )
    client_hardware_label: Optional[str] = field(
        init=True, metadata={"api_name": "cliHwLabel"}, default=None
    )
    client_installation_id: Optional[str] = field(
        init=True, metadata={"api_name": "cliInstallationId"}, default=None
    )
    client_language: Optional[str] = field(
        init=True, metadata={"api_name": "cliLang"}, default=None
    )
    client_network_ip_address: Optional[str] = field(
        init=True, metadata={"api_name": "cliNetworkIpAddress"}, default=None
    )
    client_os_user_name: Optional[str] = field(
        init=True, metadata={"api_name": "cliOSUserName"}, default=None
    )
    client_os: Optional[str] = field(init=True, metadata={"api_name": "cliOs"}, default=None)
    client_process_id: Optional[str] = field(
        init=True, metadata={"api_name": "cliProcessId"}, default=None
    )
    client_version: Optional[str] = field(
        init=True, metadata={"api_name": "cliVersion"}, default=None
    )
    consume_duration_ended_at: Optional[datetime] = field(
        init=True,
        metadata={"api_name": "consumeDurationEndedAt", "transform": "datetime"},
        default=None,
    )
    consume_duration_granted_at: Optional[datetime] = field(
        init=True,
        metadata={"api_name": "consumeDurationGrantedAt", "transform": "datetime"},
        default=None,
    )
    created: Optional[datetime] = field(init=True, metadata={"transform": "datetime"}, default=None)
    id: Optional[int] = None
    last_heartbeat: Optional[datetime] = field(
        init=True,
        metadata={"api_name": "lastHeartbeat", "transform": "datetime"},
        default=None,
    )
    lease_id: Optional[str] = field(init=True, metadata={"api_name": "leaseId"}, default=None)
    license: Optional[License] = field(
        init=True, metadata={"transform": "type", "type": License}, default=None
    )
    license_consumer: Optional[LicenseConsumer] = field(
        init=True,
        metadata={
            "api_name": "licenseConsumer",
            "transform": "type",
            "type": LicenseConsumer,
        },
        default=None,
    )
    locked: Optional[bool] = None
    modified: Optional[datetime] = field(
        init=True, metadata={"transform": "datetime"}, default=None
    )
    quantity_pre_allocated: Optional[int] = field(
        init=True, metadata={"api_name": "qtyPreAlloc"}, default=None
    )
    request_ip_address: Optional[str] = field(
        init=True, metadata={"api_name": "requestIpAddress"}, default=None
    )
    triggered_seat_use: Optional[bool] = field(
        init=True, metadata={"api_name": "triggeredSeatUse"}, default=None
    )
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
    verified_quantity: Optional[int] = field(
        init=True, metadata={"api_name": "verifiedQty"}, default=None
    )
