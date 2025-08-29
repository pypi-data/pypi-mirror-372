"""Enforced License Checkout Client."""

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


class EnforcedLicenseCheckoutClient(LicenseCheckoutClient):
    """Client for checking out licenses using an enforced model."""

    def checkout(
        self,
        to_checkout: Sequence[LicenseCheckoutArguments],
        license_key: Optional[str] = None,
        license_consumer_id: Optional[UUID] = None,
        client_details: Optional[ClientDetails] = None,
    ) -> Sequence[LicenseToken]:
        """Checkout a license.

        Args:
            to_checkout:
                List of arguments objects describing the options when checking out each license.
            license_key: Scale License Key identifying licence(s) to checkout.
            license_consumer_id: Sets a header identifying the license consumer.
            client_details: Client claims object for checkout.

        Returns:
            List of license tokens representing successful and failed license checkouts.

        Raises:
            ApiError: Checkout request failed.
        """
        return self._start(
            "checkout",
            to_checkout,
            license_key,
            license_consumer_id,
            client_details,
        )

    def release(
        self,
        to_release: Sequence[LicenseReleaseArguments],
        license_key: Optional[str] = None,
        license_consumer_id: Optional[UUID] = None,
        client_details: Optional[ClientDetails] = None,
    ) -> Sequence[LicenseReleaseResult]:
        """Release a license.

        Args:
            to_release: List of arguments objects describing the licenses to release.
            license_key: Scale License Key identifying licence(s) to release.
            license_consumer_id: Sets a header identifying the license consumer.
            client_details: Client claims object for release.

        Returns:
            List of LicenseReleaseResult objects representing the licenses successfully released.

        Raises:
            ApiError: Release request failed.
        """
        return self._end("release", to_release, license_key, license_consumer_id, client_details)

    def heartbeat(
        self,
        to_heartbeat: Sequence[LicenseHeartbeatArguments],
        license_key: Optional[str] = None,
        license_consumer_id: Optional[UUID] = None,
        client_details: Optional[ClientDetails] = None,
    ) -> Sequence[LicenseToken]:
        """Verify one or more license checkout is still valid.

        Args:
            to_heartbeat: List of arguments objects describing the licenses to heartbeat.
            license_key: Scale License Key identifying licence(s) to heartbeat.
            license_consumer_id: Sets a header identifying the license consumer.
            client_details: Client claims object for heartbeat.

        Returns:
            List of LicenseToken objects for the successful and failed heartbeats.

        Raises:
            ApiError: Heartbeat request failed.
        """
        return self._heartbeat(
            "heartbeat", to_heartbeat, license_key, license_consumer_id, client_details
        )

    def checkout_single_by_license_key(
        self,
        license_key: str,
        to_checkout: LicenseCheckoutArguments,
        client_details: Optional[ClientDetails] = None,
    ) -> LicenseToken:
        """Checkout a license by license key.

        Args:
            license_key: Scale License Key identifying licence(s) to checkout.
            to_checkout: An object describing the options for checking out the license.
            client_details: Client claims object for checkout.

        Returns:
            A license token describing the success or failure of the checkout.

        Raises:
            ApiError: Checkout request failed.
        """
        tokens = self._start("checkout", [to_checkout], license_key, client_details=client_details)
        return tokens[0]

    def checkout_multiple_by_license_key(
        self,
        license_key: str,
        to_checkout: Sequence[LicenseCheckoutArguments],
        client_details: Optional[ClientDetails] = None,
    ) -> Sequence[LicenseToken]:
        """Checkout multiple licenses using a license key.

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
        return self._start("checkout", to_checkout, license_key, client_details=client_details)

    def release_single_by_license_key(
        self,
        license_key: str,
        args: LicenseReleaseArguments,
        client_details: Optional[ClientDetails] = None,
    ) -> LicenseReleaseResult:
        """Release a license by license key.

        Args:
            license_key: Scale License Key identifying licence(s) to release.
            args: An arguments object describing the license to release.
            client_details: Client claims object for release.

        Returns:
            LicenseReleaseResult object representing the license released.

        Raises:
            ApiError: Release request failed.
        """
        release_results = self._end(
            "release", [args], license_key=license_key, client_details=client_details
        )
        return release_results[0]

    def release_multiple_by_license_key(
        self,
        license_key: str,
        to_release: Sequence[LicenseReleaseArguments],
        client_details: Optional[ClientDetails] = None,
    ) -> Sequence[LicenseReleaseResult]:
        """Release multiple licenses by license key.

        Args:
            license_key: Scale License Key identifying licence(s) to release.
            to_release: List of arguments objects describing the licenses to release.
            client_details: Client claims object for release.

        Returns:
            List of LicenseReleaseResult objects representing the licenses successfully released.

        Raises:
            ApiError: Release request failed.
        """
        return self._end(
            "release", args=to_release, license_key=license_key, client_details=client_details
        )

    def heartbeat_single_by_license_key(
        self,
        license_key: str,
        to_heartbeat: LicenseHeartbeatArguments,
        client_details: Optional[ClientDetails] = None,
    ) -> LicenseToken:
        """Heartbeat a license by license key.

        Args:
            license_key: Scale License Key identifying licence(s) to heartbeat.
            to_heartbeat: An arguments object describing the license to heartbeat.
            client_details: Client claims object for heartbeat.

        Returns:
            LicenseToken object describing the successful or failed heartbeat attempt.

        Raises:
            ApiError: Heartbeat request failed.
        """
        heartbeat_results = self._heartbeat(
            "heartbeat", [to_heartbeat], license_key=license_key, client_details=client_details
        )
        return heartbeat_results[0]

    def heartbeat_multiple_by_license_key(
        self,
        license_key: str,
        to_heartbeat: Sequence[LicenseHeartbeatArguments],
        client_details: Optional[ClientDetails] = None,
    ) -> Sequence[LicenseToken]:
        """Heartbeat multiple licenses by license key.

        Args:
            license_key: Scale License Key identifying licence(s) to heartbeat.
            to_heartbeat:
                List of arguments objects describing the licenses to heartbeat.
            client_details: Client claims object for heartbeat.

        Returns:
            List of LicenseToken objects for the successful and failed heartbeats.

        Raises:
            ApiError: Heartbeat request failed.
        """
        return self._heartbeat(
            "heartbeat",
            args=to_heartbeat,
            license_key=license_key,
            client_details=client_details,
        )
