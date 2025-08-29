"""License token store."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Union

from .license_token import LicenseToken


def _to_lease_ids(maybe_tokens):
    return [
        lease_id
        for maybe_token in maybe_tokens
        if (
            lease_id := maybe_token.lease_id
            if isinstance(maybe_token, LicenseToken)
            else maybe_token
        )
    ]


class TokenStoreABC(ABC):
    """License token store base class.

    This type defines the methods that will be used to read, persist, and delete
    license tokens.

    These methods are called by :class:`tenduke_scale.license_checkout.LicenseCheckoutClient`
    and its subclasses to load, store, and delete
    :class:`tenduke_scale.license_checkout.LicenseToken` instances based on the operations called on
    the client.
    """

    @abstractmethod
    def save(self, tokens: Sequence[LicenseToken]):
        """Save LicenseTokens to the store.

        This operation should be additive.

        Args:
            tokens: List of tokens to save. This should be interpretted as replacing the current
                    contents of the store.
        """

    @abstractmethod
    def load(self) -> Sequence[LicenseToken]:
        """Load any currently stored LicenseTokens.

        Returns:
            The sequence of LicenseTokens currently stored or persisted in the token store.
        """

    @abstractmethod
    def remove_all(self):
        """Clear the contents of the store."""

    def remove(self, to_remove: Union[Sequence[str], Sequence[LicenseToken]]):
        """Remove the specified LicenseTokens, by lease id or by token.

        Args:
            to_remove: List of lease ids or tokens to remove from the store.
        """
        if not to_remove:
            return
        current_tokens = self.load()
        lease_ids = _to_lease_ids(to_remove)
        tokens_to_save = [token for token in current_tokens if token.lease_id not in lease_ids]
        self.remove_all()
        self.save(tokens_to_save)

    def update(
        self,
        tokens: Sequence[LicenseToken],
    ):
        """Store the new tokens and remove old tokens that there are new checkouts for.

        Args:
            tokens: List of new tokens to add to the store, replacing any previously
                    held tokens that are superseded.
        """
        keep = [
            token
            for token in self.load()
            if not any(
                new_token for new_token in tokens if new_token.old_lease_id == token.lease_id
            )
        ]
        self.remove_all()
        self.save([*keep, *tokens])


class DefaultTokenStore(TokenStoreABC):
    """Default (non-persistent) implementation of TokenStore."""

    def __init__(self):
        """Construct instance of the DefaultTokenStore."""
        self._tokens = []

    def save(self, tokens: Sequence[LicenseToken]):
        """Save LicenseTokens to the store.

        Args:
            tokens: List of tokens to save. This should be interpretted as replacing the current
                    contents of the store.
        """
        self._tokens = [*self._tokens, *tokens]

    def load(self) -> Sequence[LicenseToken]:
        """Load any currently stored LicenseTokens.

        Returns:
            The sequence of LicenseTokens currently stored or persisted in the token store.
        """
        return self._tokens

    def remove_all(self):
        """Clear the contents of the store."""
        self._tokens = []
