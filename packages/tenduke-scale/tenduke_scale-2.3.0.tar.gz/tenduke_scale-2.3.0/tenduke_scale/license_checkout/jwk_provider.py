"""JSON Web Key provider.

A wrapper for PyJWKClient that saves and loads JSON Web Key Set using configured
:class:`tenduke_scale.license_checkout.verification_key_store.VerificatioKeyStoreABC`.
"""

import json

from jwt import PyJWK, PyJWKClient

from tenduke_scale.license_checkout.verification_key_store import VerificationKeyStoreABC


class JWKProvider(PyJWKClient):
    """JSON Web Key provider."""

    def __init__(self, jwks_uri: str, store: VerificationKeyStoreABC):
        """Initialize."""
        self.jwks_uri = jwks_uri
        self._store = store
        self._loaded = False
        # lifespan: 96 hours (as seconds)
        super().__init__(self.jwks_uri, cache_keys=True, lifespan=345000)

    def _ensure_keys(self) -> None:
        """Ensure that keys are loaded from the store or fetched from the JWKS URI."""
        if self._loaded:
            return
        stored_keys = self._store.load()
        if stored_keys is not None and self.jwk_set_cache is not None:
            self.jwk_set_cache.put(json.loads(stored_keys))
            self._loaded = True

    def get_signing_key_from_jwt(self, jwt_text: str) -> PyJWK:
        """Get the JSON Web Key that signed the JWT.

        Args:
            jwt_text: Encoded JWT string.
        Returns:
            JSON Web Key instance for the key that was used to sign the JWT.
        """
        # Load any stored keys. This means that if the required key is already held locally, there
        # is no need to call the JSON Web Key Set endpoint on the server.
        self._ensure_keys()
        return super().get_signing_key_from_jwt(jwt_text)

    def fetch_data(self):
        """Fetch JSON Web Key data from the JWKS endpoint.

        This is a wrapper for PyJWKClient.fetch_data which fetches the latest keys from the server.
        Additionally, the JSON Web Key Set is saved to the configured
        :class:`tenduke_scale.license_checkout.verification_key_store.VerificatioKeyStoreABC`.
        """
        keys = super().fetch_data()
        keys_to_store = json.dumps(keys)
        # If fetch_data was called then we have a new copy of the JSON Web Key Set from the server.
        # This may contain new keys (or have removed some) so the local store should be updated.
        self._store.save(keys_to_store)
        self._loaded = True
        return keys
