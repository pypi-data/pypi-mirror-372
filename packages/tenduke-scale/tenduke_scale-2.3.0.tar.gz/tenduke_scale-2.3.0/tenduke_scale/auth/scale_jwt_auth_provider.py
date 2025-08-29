"""Authorization implementations for requests to 10Duke Scale API usine JWT authorization."""

import time
from dataclasses import dataclass

# conditional import for Python versions <= 3.10
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone

    UTC = timezone.utc

from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from jwt import encode
from requests import PreparedRequest
from requests.auth import AuthBase
from tenduke_core.config import TendukeConfig

from tenduke_scale.exceptions.validation import (
    InvalidClaimsError,
    MissingClaimError,
    MissingValiditySecondsError,
)


@dataclass
class ScaleJwtClaims:
    """Claims for Scale JWT.

    https://docs.scale.10duke.com/api/api-authorization/#confidential-applications-10duke-jwts

    Attributes:
        sub: Subject, used to identify calling identity. The value is matched to
             connectedIdentityId field in LicenseConsumer objects.
        iss: Issuer of the token.
        valid_for: Number of seconds the token should be considered valid for.
        permissions: Array, value syntax: [Resource.permission,...].
        license_consumer_id: The id of the consumer of the license.
    """

    sub: str
    iss: str
    valid_for: timedelta
    permissions: Sequence[str] = "*.*"
    license_consumer_id: Optional[UUID] = None


def _validate_claims(claims):
    try:
        if not claims.sub:
            raise MissingClaimError("sub", "Subject")
        if not claims.iss:
            raise MissingClaimError("iss", "Issuer")
        if not claims.permissions:
            raise MissingClaimError("permissions", "Permissions")
        if not claims.valid_for.seconds:
            raise MissingValiditySecondsError()
    except AttributeError as exc:
        raise InvalidClaimsError() from exc


def _get_payload(claims):
    now_epoch = int(time.time())
    expires_epoch = now_epoch + claims.valid_for.seconds
    payload = {
        "jti": str(uuid4()),
        "iat": now_epoch,
        "sub": claims.sub,
        "iss": claims.iss,
        "exp": expires_epoch,
        "permissions": claims.permissions,
    }
    if claims.license_consumer_id:
        payload["lcid"] = str(claims.license_consumer_id)
    return payload


class ScaleJwtAuth(AuthBase):
    """Scale JWT Auth hook - for use in confidential applications."""

    def __init__(
        self,
        key_id: str,
        private_key: str,
        claims: ScaleJwtClaims,
        config: TendukeConfig,
    ) -> None:
        """Construct a ScaleJwtAuth provider (hook).

        Args:
            key_id: The id of the key pair to use to sign the JWT.
            private_key: The private half of of the key pair to use to sign the JWT.
            claims: The authorization claims to be included in the JWT.
            config: Configuration object specifying token_refresh_leeway_seconds.
        """
        _validate_claims(claims)
        self._key_id = key_id
        self._private_key = private_key
        self._claims = claims
        self._make_jwt()
        self._token_leeway_seconds = config.token_refresh_leeway_seconds

    def _make_jwt(self):
        payload = _get_payload(self._claims)
        self._expiry = datetime.fromtimestamp(payload["exp"], UTC)
        self.jwt = encode(
            payload, self._private_key, algorithm="RS256", headers={"kid": self._key_id}
        )

    def __call__(self, r: PreparedRequest):
        """Mutate outgoing request (adding authorization header).

        Args:
            r: Outgoing request.
        """
        if (self._expiry - datetime.now(UTC)).total_seconds() < self._token_leeway_seconds:
            self._make_jwt()
        r.headers["Authorization"] = f"ScaleJwt {self.jwt}"
        return r

    def __eq__(self, other):
        """Return True if instances are equal; otherwise False.

        Equality is tested by comparing the JWTs.
        """
        return self.jwt == getattr(other, "jwt", None)

    def __ne__(self, other):
        """Return True if instances are not equal; otherwise False.

        Equality is tested by comparing the JWTs.
        """
        return not self == other
