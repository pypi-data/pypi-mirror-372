"""Feature flags as JWT."""

# conditional import for Python versions <= 3.10
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone

    UTC = timezone.utc

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

import jwt

from .feature_flags_response import FeatureFlagsResponse


class FeatureFlagsToken:
    """Feature flags token."""

    def __init__(self, raw_jwt, public_key):
        """Construct an instance of the FeatureFlagsToken from a JWT and public key.

        Args:
            raw_jwt: The base64 encoded string containing the token.
            public_key: The public part of the key pair used to sign the token.
        """
        self._jwt = raw_jwt
        self._public_key = public_key
        self._claims = jwt.decode(raw_jwt, public_key, algorithms=["RS256"])

    @property
    def issued_at_time(self) -> datetime:
        """When was the token issued: Issued at time (iat)."""
        return datetime.fromtimestamp(self._claims["iat"], UTC)

    @property
    def jwt_id(self) -> str:
        """Identifier of the token: JWT Id (jti)."""
        return self._claims["jti"]

    @property
    def issuer(self) -> str:
        """Who issued the token: Issuer (iss)."""
        return self._claims["iss"]

    @property
    def expires(self) -> datetime:
        """When does the token expire: Expiry (exp)."""
        return datetime.fromtimestamp(self._claims["exp"], UTC)

    @property
    def not_before(self) -> datetime:
        """When does the token become valid: Not Before (nbf)."""
        return datetime.fromtimestamp(self._claims["nbf"], UTC)

    @property
    def licensee_id(self) -> UUID:
        """The licensee the features are for."""
        return UUID(self._claims["licenseeId"])

    @property
    def license_consumer_id(self) -> UUID:
        """The license consumer (user) the features are licensed to."""
        return UUID(self._claims["licenseConsumerId"])

    @property
    def feature_flags_dict(self) -> dict[str, list[str]]:
        """The features as a dict keyed on product name."""
        return self._claims["featureFlags"]

    @property
    def feature_flags(self) -> Sequence[FeatureFlagsResponse]:
        """The features as a list of FeatureFlagsResponse objects."""
        return [
            FeatureFlagsResponse(product_name=k, features=v)
            for k, v in self._claims["featureFlags"].items()
        ]
