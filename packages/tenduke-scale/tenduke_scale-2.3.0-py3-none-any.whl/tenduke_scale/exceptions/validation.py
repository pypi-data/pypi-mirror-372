"""Validation Errors."""


class InvalidClaimsError(TypeError):
    """The claims are missing a required attribute."""

    def __init__(self):
        """Construct an InvalidClaimsError instance."""
        super().__init__("Valid claims must be provided to generate authorization token.")


class MissingClaimError(ValueError):
    """A required claim has no value."""

    def __init__(self, name: str, label: str):
        """Construct a MissingClaimError instance.

        Args:
            name:  name of the missing claim.
            label: label of the missing claim.
        """
        # Subject (sub)
        super().__init__(f"{label} ({name}) claim must be provided.")


class MissingValiditySecondsError(ValueError):
    """Validity seconds not provided in recognised format."""

    def __init__(self):
        """Construct a MissingValiditySecondsError instance."""
        super().__init__("valid_for must provide validity period seconds.")


class HeartbeatTooEarlyError(ValueError):
    """Heartbeat attempted too early."""

    def __init__(self):
        """Construct a HeartbeatTooEarlyError instance."""
        super().__init__("Heartbeat too early for one or more tokens, see hbnbf time on token(s).")


class InvalidLicenseKeyError(ValueError):
    """License key contains invalid characters."""

    def __init__(self):
        """Construct an InvalidLicenseKeyError instance."""
        super().__init__("Invalid format for License Key.")


class InvalidJWKUriError(ValueError):
    """URI for the JWKS endpoint is invalid."""

    def __init__(self, uri: str):
        """Construct an InvalidJWKUriError instance."""
        msg = f"Unable to parse hostname from URL string: {uri}. Please provide a full URI."
        super().__init__(msg)
