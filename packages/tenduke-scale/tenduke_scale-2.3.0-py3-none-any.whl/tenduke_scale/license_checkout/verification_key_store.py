"""Service for serializing and deserializing JSON Web Key Set used to verify license tokens."""

import os
from abc import ABC, abstractmethod
from urllib.parse import urlparse

from platformdirs import user_data_dir

from tenduke_scale.exceptions.validation import InvalidJWKUriError


class VerificationKeyStoreABC(ABC):
    """Verification store base class.

    This type defines the methods that will be used to read and delete keys for verifying license
    tokens.

    These methods are called by :class:`tenduke_scale.license_checkout.LicenseCheckoutClient` to
    save and load the keys used to verify the :class:`tenduke_scale.license_checkout.LicenseToken`
    instances parsed from JWT received from the 10Duke Scale API.
    """

    @abstractmethod
    def load(self) -> str | None:
        """Load the keys from the store.

        Returns:
            The JSON Web Key Set.
        """

    @abstractmethod
    def save(self, keys_as_json: str) -> None:
        """Save the keys to the store.

        Args:
            keys_as_json: JSON Web Key Set response body. This should be interpretted as replacing
                          the current contents of the store.
        """


class DefaultVerificationKeyStore(VerificationKeyStoreABC):
    """Default implementation of the VerificationKeyStore.

    The keys are stored in the local application data folder of the file system.
    """

    def __init__(self, app_author: str, app_name: str, jwks_host_uri: str):
        """Initialize."""
        self._app_author = app_author
        self._app_name = app_name
        parsed = urlparse(jwks_host_uri)
        # hostname gives tld plus sub-domains
        # netloc includes any credentials and the port if explicitly - we don't want those in a
        # file name we save to disk
        host = parsed.hostname
        if host is None:
            raise InvalidJWKUriError(jwks_host_uri)
        self._file_name = f"{host}.json"

    def load(self) -> str | None:
        """Load the keys from the store.

        Returns:
            The JSON Web Key Set.
        """
        file_content = None
        folder_name = user_data_dir(self._app_author, self._app_name)
        store_file_name = f"{folder_name}/{self._file_name}"
        if os.path.exists(store_file_name):
            with open(store_file_name, encoding="utf-8") as file:
                file_content = file.read()
        return file_content

    def save(self, keys_as_json: str) -> None:
        """Save the keys to the store.

        Args:
            keys_as_json: JSON Web Key Set response body. This should be interpretted as replacing
                          the current contents of the store.
        """
        folder_name = user_data_dir(self._app_author, self._app_name)
        os.makedirs(folder_name, exist_ok=True)
        store_file_name = f"{folder_name}/{self._file_name}"
        with open(store_file_name, "w", encoding="utf-8") as file:
            file.write(keys_as_json)
