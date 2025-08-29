"""License token model."""

# conditional import for Python versions <= 3.10
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone

    UTC = timezone.utc

from collections.abc import Sequence
from datetime import datetime
from typing import Any, Optional, TypeVar

import jwt

from ..licensing import QuantityDimension
from .license_release_arguments import LicenseReleaseArguments

QD = QuantityDimension

T = TypeVar("T", bound="LicenseToken")


class LicenseToken:
    """License token model."""

    def __init__(self, raw_jwt: str, public_key: str):
        """Construct an instance of a LicenseToken from a JWT and public key.

        Args:
            raw_jwt: The base64 encoded string containing the token.
            public_key: The public part of the key pair used to sign the token.
        """
        self.raw_jwt = raw_jwt
        self._public_key = public_key
        self._claims = jwt.decode(raw_jwt, public_key, algorithms=["RS256"])

    @property
    def lease_id(self) -> Optional[str]:
        """Lease id, used to refresh or release license."""
        return self._claims.get("leaseId")

    @property
    def product_name(self) -> str:
        """Product name, identifies what permission is granted."""
        return self._claims["productName"]

    @property
    def features(self) -> str:
        """Features, lists sub features granted in this license."""
        return self._claims["features"]

    @property
    def quantity(self) -> int:
        """Number of seats, uses, or time granted."""
        return self._claims["qty"]

    @property
    def quantity_dimension(self) -> QD:
        """Describes whether this is seats, uses, or use time."""
        return QuantityDimension[self._claims["qtyDimension"]]

    @property
    def jwt_id(self) -> str:
        """JWT Id (jti) claim."""
        return self._claims["jti"]

    @property
    def claims(self) -> dict[str, Any]:
        """Raw claims from JWT."""
        return self._claims

    @property
    def heartbeat_not_before(self) -> datetime:
        """Heartbeat not before (hbnbf) claim."""
        return datetime.fromtimestamp(self._claims["hbnbf"], UTC)

    @property
    def old_lease_id(self) -> Optional[str]:
        """Old lease id (if this is a continuation of a previous lease)."""
        return self._claims.get("oldLeaseId")

    @property
    def status(self) -> Optional[str]:
        """Status of checkout."""
        return self._claims.get("status")

    @property
    def error_code(self) -> Optional[str]:
        """Error code for a failed consumtpion."""
        return self._claims.get("errorCode")

    @property
    def error_description(self) -> Optional[str]:
        """Error description for a failed consumtpion."""
        return self._claims.get("errorDescription")

    def to_release_argument(
        self, final_quantity_used: Optional[int] = None
    ) -> Optional[LicenseReleaseArguments]:
        """Construct a LicenseReleaseArgument, if this was a successful checkout.

        Args:
            final_quantity_used: Specifies the quantity to send in the release call.

        Returns:
            LicenseReleaseArguments object to release the lease represented by this license token.
            If this license token is for a failed or unsuccessful checkout, then the method returns
            None.
        """
        return (
            LicenseReleaseArguments(lease_id=self.lease_id, final_quantity_used=final_quantity_used)
            if self.lease_id
            else None
        )

    @classmethod
    def make_release_arguments(
        cls: type[T], tokens: Sequence[T]
    ) -> Sequence[LicenseReleaseArguments]:
        """Return LicenseReleaseArguments for successful checkouts.

        Any license tokens representing failed or unsuccessful checkouts are dropped from the
        returned sequence.

        Args:
            tokens: List of license tokens that may include one or more successful checkouts.

        Returns:
            Sequence of LicenseReleaseArguments that can be used to release the license tokens that
            represent successful checkouts.
        """
        return [arg for token in tokens if (arg := token.to_release_argument()) is not None]
