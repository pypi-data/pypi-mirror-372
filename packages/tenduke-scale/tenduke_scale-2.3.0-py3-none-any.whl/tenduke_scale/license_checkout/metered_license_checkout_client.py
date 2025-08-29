"""Metered License Checkout Client."""

from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from .client_details import ClientDetails
from .license_checkout_arguments import LicenseCheckoutArguments
from .license_checkout_client import LicenseCheckoutClient
from .license_heartbeat_arguments import LicenseHeartbeatArguments
from .license_release_arguments import LicenseReleaseArguments
from .license_release_result import LicenseReleaseResult
from .license_token import LicenseToken


class MeteredLicenseCheckoutClient(LicenseCheckoutClient):
    """Client for consuming licenses using a metered use model."""

    def start(
        self,
        to_checkout: Sequence[LicenseCheckoutArguments],
        license_key: Optional[str] = None,
        license_consumer_id: Optional[UUID] = None,
        client_details: Optional[ClientDetails] = None,
    ) -> Sequence[LicenseToken]:
        """Start metered license use.

        Metered use of a license is based on the product name and a signal that use of the license
        has started (calling this method).
        A license ID can optionally be specified to record usage of a specific license.

        Args:
            to_checkout:
                List of arguments objects describing the options when checking out each license.
            license_key: Scale License Key identifying licence(s) to checkout.
            license_consumer_id:
                Sets a header identifying the license consumer. Mandatory if using Scale JWT API
                authorization; otherwise optional.
            client_details: Client claims object for checkout.

        Returns:
            List of license tokens representing successful and failed license checkouts.

        Raises:
            ApiError: Checkout request failed.
        """
        return self._start(
            "start-metered-use",
            to_checkout,
            license_key,
            license_consumer_id,
            client_details,
        )

    def end(
        self,
        to_release: Sequence[LicenseReleaseArguments],
        license_key: Optional[str] = None,
        license_consumer_id: Optional[UUID] = None,
        client_details: Optional[ClientDetails] = None,
    ) -> Sequence[LicenseReleaseResult]:
        """End metered license use.

        Ending metered use must send the final used quantity, which is recorded by the API as part
        of ending the metered usage session.

        Args:
            to_release:
                List of arguments objects describing the options when releasing each license.
            license_key: Scale License Key identifying licence(s) to release.
            license_consumer_id:
                Sets a header identifying the license consumer. Mandatory if using Scale JWT API
                authorization; otherwise optional.
            client_details:
                Client claims object for End.

        Returns:
            List of LicenseReleaseResult objects representing the licenses successfully released.

        Raises:
            ApiError: Release request failed.
        """
        return self._end(
            "end-metered-use", to_release, license_key, license_consumer_id, client_details
        )

    def heartbeat(
        self,
        to_heartbeat: Sequence[LicenseHeartbeatArguments],
        license_key: Optional[str] = None,
        license_consumer_id: Optional[UUID] = None,
        client_details: Optional[ClientDetails] = None,
    ) -> Sequence[LicenseToken]:
        """Update the consumed quantity for a license.

        The heartbeat operation also re-authorizes the use of a license.

        Args:
            to_heartbeat: List of arguments objects describing the licenses to heartbeat.
            license_key: Scale License Key identifying licence(s) to heartbeat.
            license_consumer_id:
                Sets a header identifying the license consumer. Mandatory if using Scale JWT API
                authorization; otherwise optional.
            client_details:
                Client claims object for Heartbeat.

        Returns:
            List of LicenseToken objects for the successful and failed heartbeats.

        Raises:
            ApiError: Heartbeat request failed.
        """
        return self._heartbeat(
            "heartbeat-metered-use", to_heartbeat, license_key, license_consumer_id, client_details
        )

    def start_single_by_license_key(
        self,
        license_key: str,
        to_checkout: LicenseCheckoutArguments,
        client_details: Optional[ClientDetails] = None,
    ) -> LicenseToken:
        """Start use of a single license using a license key.

        Args:
            license_key: Scale License Key identifying licence(s) to checkout.
            to_checkout: An object describing the options for checking out the license.
            client_details: Client claims object for checkout.

        Returns:
            A license token describing the success or failure of the checkout.

        Raises:
            ApiError: Checkout request failed.
        """
        tokens = self._start(
            "start-metered-use",
            [to_checkout],
            license_key,
            client_details=client_details,
        )
        return tokens[0]

    def start_multiple_by_license_key(
        self,
        license_key: str,
        to_checkout: Sequence[LicenseCheckoutArguments],
        client_details: Optional[ClientDetails] = None,
    ) -> Sequence[LicenseToken]:
        """Start use of a multiple licenses using a license key.

        Args:
            license_key: Scale License Key identifying licence(s) to checkout.
            to_checkout:
                A list of objects describing the options for checking out the licenses.
            client_details: Client claims object for checkout.

        Returns:
            List of license tokens representing successful and failed license checkouts.

        Raises:
            ApiError: Checkout request failed.
        """
        return self._start(
            "start-metered-use",
            to_checkout,
            license_key,
            client_details=client_details,
        )

    def end_single_by_license_key(
        self, license_key: str, to_end: LicenseReleaseArguments
    ) -> LicenseReleaseResult:
        """End metered use of a single license using a license key.

        Args:
            license_key: Scale License Key identifying licence(s) to release.
            to_end: An arguments object describing the license to release.

        Returns:
            LicenseReleaseResult object representing the license released.

        Raises:
            ApiError: Release request failed.
        """
        release_results = self._end("end-metered-use", [to_end], license_key=license_key)
        return release_results[0]

    def end_multiple_by_license_key(
        self, license_key: str, to_end: Sequence[LicenseReleaseArguments]
    ) -> Sequence[LicenseReleaseResult]:
        """End metered use of a multiple licenses using a license key.

        Args:
            license_key: Scale License Key identifying licence(s) to release.
            to_end: List of arguments objects describing the licenses to release.

        Returns:
            List of LicenseReleaseResult objects representing the licenses successfully released.

        Raises:
            ApiError: Release request failed.
        """
        return self._end("end-metered-use", to_end, license_key=license_key)

    def heartbeat_single_by_license_key(
        self, license_key: str, to_heartbeat: LicenseHeartbeatArguments
    ) -> LicenseToken:
        """Heartbeat a license by license key.

        Args:
            license_key: Scale License Key identifying licence(s) to heartbeat.
            to_heartbeat: An arguments object describing the license to heartbeat.

        Returns:
            LicenseToken object describing the successful or failed heartbeat attempt.

        Raises:
            ApiError: Heartbeat request failed.
        """
        heartbeat_results = self._heartbeat(
            "heartbeat-metered-use", [to_heartbeat], license_key=license_key
        )
        return heartbeat_results[0]

    def heartbeat_multiple_by_license_key(
        self,
        license_key: str,
        to_heartbeat: Sequence[LicenseHeartbeatArguments],
    ) -> Sequence[LicenseToken]:
        """Heartbeat multiple licenses by license key.

        Args:
            license_key: Scale License Key identifying licence(s) to heartbeat.
            to_heartbeat:
                List of arguments objects describing the licenses to heartbeat.

        Returns:
            List of LicenseToken objects for the successful and failed heartbeats.

        Raises:
            ApiError: Heartbeat request failed.
        """
        return self._heartbeat(
            "heartbeat-metered-use",
            args=to_heartbeat,
            license_key=license_key,
        )
