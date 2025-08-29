"""License checkout client."""

import datetime
import re
from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from requests import HTTPError, Session
from tenduke_core.auth.auth_provider import IdTokenAuth
from tenduke_core.exceptions import map_error
from tenduke_core.exceptions.validation import InvalidArgumentError

from tenduke_scale.exceptions.validation import HeartbeatTooEarlyError, InvalidLicenseKeyError
from tenduke_scale.license_checkout.jwk_provider import JWKProvider

from ..describe_license_options import DescribeLicenseOptions
from ..licensing import License, LicenseConsumer
from ..paging import PagingOptions
from .client_details import ClientDetails
from .feature_flags_response import FeatureFlagsResponse
from .feature_flags_token import FeatureFlagsToken
from .license_checkout_arguments import LicenseCheckoutArguments
from .license_consumer_client_binding_status import LicenseConsumerClientBindingStatus
from .license_consumer_licenses_status import LicenseConsumerLicensesStatus
from .license_heartbeat_arguments import LicenseHeartbeatArguments
from .license_release_arguments import LicenseReleaseArguments
from .license_release_result import LicenseReleaseResult
from .license_token import LicenseToken
from .token_store import DefaultTokenStore, TokenStoreABC
from .verification_key_store import DefaultVerificationKeyStore, VerificationKeyStoreABC


def raise_for_response(response, uri):
    """Translate HTTP code to error.

    Args:
        response: Potentially failed response object.
        uri: The URI that was requested.

    Raises:
        ApiError: The response is an error response.
    """
    try:
        response.raise_for_status()
    except HTTPError as exc:
        _map_error(exc, uri, response)


def _map_error(exc, uri, response):
    code = response.status_code
    ex = map_error(code)
    raise ex(uri=uri, response=response) from exc


def _concat_checkout_headers(
    client_details: Optional[ClientDetails], license_consumer_id: Optional[UUID]
):
    client = client_details.to_api() if client_details else {}
    consumer = {"licenseConsumerId": str(license_consumer_id)} if license_consumer_id else {}
    return {**client, **consumer}


def _license_key_fragment(license_key):
    if license_key is None:
        return ""
    if re.fullmatch("[a-zA-Z0-9\\-_]{16,64}", license_key) is not None:
        return f"/{license_key}"
    raise InvalidLicenseKeyError()


def _make_request(session, host, path, **kwargs):
    """Make a describe request and process any error response."""
    paging_args = kwargs.pop("paging_args", None)
    builder = _DescribeQueryStringBuilder()
    query_string = builder.build(**kwargs)
    uri = f"{host}{path}{query_string}"
    headers = paging_args.to_api() if paging_args is not None else {}
    response = session.get(uri, headers=headers)
    raise_for_response(response, uri)
    return response


def _describe_request_json(session, host, path, **kwargs):
    """Make a describe request and return body json."""
    response = _make_request(session, host, path, **kwargs)
    return response.json()


def _describe_request_text(session, host, path, **kwargs):
    """Make a describe request and return body text."""
    response = _make_request(session, host, path, **kwargs)
    return response.text


class _DescribeQueryStringBuilder:
    """Helper class to build query string for describe methods."""

    def __init__(self):
        self.map = {
            "licensee_id": self.licensee_fragment,
            "license_consumer_id": self.license_consumer_fragment,
            "license_id": self.license_id_fragment,
            "describe_license_options": self.describe_license_options_fragment,
            "client_binding_id": self.client_binding_id_fragment,
            "with_metadata": self.with_metadata_fragment,
            "filter_value": self.filter_value_fragment,
            "license_key": self.license_key_fragment,
        }

    def licensee_fragment(self, licensee_id):
        """Fragment based on licensee id."""
        return f"licenseeId={licensee_id}"

    def license_consumer_fragment(self, license_consumer_id):
        """Fragment based on license consumer id."""
        return None if license_consumer_id is None else f"licenseConsumerId={license_consumer_id}"

    def license_id_fragment(self, license_id):
        """Fragment based on license id."""
        return None if license_id is None else f"licenseId={license_id}"

    def describe_license_options_fragment(self, describe_license_options):
        """Fragment based on describe license options."""
        return (
            None if describe_license_options is None else describe_license_options.to_query_string()
        )

    def client_binding_id_fragment(self, client_binding_id):
        """Fragment based on client binding id."""
        return "" if client_binding_id is None else f"clientBindingId={client_binding_id}"

    def with_metadata_fragment(self, with_metadata):
        """Fragment based on with metadata parameter."""
        return (
            None
            if with_metadata is None
            else f"withMetadata={'true' if with_metadata else 'false'}"
        )

    def filter_value_fragment(self, filter_value):
        """Fragment based on filter value parameter."""
        return None if filter_value is None else f"filterValue={filter_value}"

    def license_key_fragment(self, license_key):
        """Fragment based on license key query parameter."""
        return None if license_key is None else f"licenseKey={license_key}"

    def build(self, **kwargs):
        """Build query string parameters from variable list of kwargs."""
        fragments = [
            fragment
            for k, v in kwargs.items()
            if (fragment := self.map.get(k, lambda value: None)(v)) is not None
        ]
        not_null = [x for x in fragments if x]
        if any(not_null):
            combined = "&".join(not_null)
            return f"?{combined}"
        return ""


class LicenseCheckoutClient:
    """Base class for license checkout clients."""

    start_action = "checkout"
    end_action = "release"
    heartbeat_action = "heartbeat"

    def __init__(
        self,
        api_url: str,
        session: Session,
        token_store: TokenStoreABC | None = None,
        verification_key_store: VerificationKeyStoreABC | None = None,
    ):
        """Construct the LicenseCheckoutClient.

        Args:
            api_url: Base API URL of the Scale tenant being accessed.
            session: requests.Session object configured for use by client.
            token_store: Used to store and manage tokens.
            verification_key_store: Used to save and load public keys for license token verification.
        """
        self.api_url = api_url
        jwks_uri = f"{api_url}/licensing-signing-keys/.well-known/jwks.json"
        store = verification_key_store or DefaultVerificationKeyStore("10Duke", "Scale", api_url)
        self._jwk_client = JWKProvider(jwks_uri, store)
        self.session = session
        self.store = token_store or DefaultTokenStore()
        self._client_details: Optional[ClientDetails] = None

    def describe_licensees(
        self,
        license_consumer_id: Optional[UUID] = None,
        paging_args: Optional[PagingOptions] = None,
    ) -> Sequence[LicenseConsumer]:
        """Retrieve the set of licensees that the consumer is connected to.

        Args:
            license_consumer_id: The license consumer to describe licensees for.
            paging_args: Sets limit, offset, and sorting for the result.

        Returns:
            List of license consumer objects describing the licensees that the consumer can access
            licenses from.

        Raises:
            ApiError: The request failed.
        """
        path = "/licensing/actions/describe-license-consumer-licensees"
        json = _describe_request_json(
            self.session,
            self.api_url,
            path,
            license_consumer_id=license_consumer_id,
            paging_args=paging_args,
        )
        return [LicenseConsumer.from_api(item) for item in json]

    def describe_licenses(
        self,
        licensee_id: UUID,
        license_consumer_id: Optional[UUID] = None,
        describe_license_options: Optional[DescribeLicenseOptions] = None,
        paging: Optional[PagingOptions] = None,
    ) -> LicenseConsumerLicensesStatus:
        """Retrieve the licenses the license consumer currently has access to from the licensee.

        Args:
            licensee_id: The licensee to describe licenses for.
            license_consumer_id: The license consumer to describe licenses for.
            describe_license_options: Options setting what information to return.
            paging: Sets limit, offset, and sorting for the result.

        Returns:
            LicenseConsumerLicensesStatus listing the licenses that the consumer has access to.

        Raises:
            ApiError: The request failed.
        """
        path = "/licensing/actions/describe-license-consumer-licenses"
        json = _describe_request_json(
            self.session,
            self.api_url,
            path,
            paging_args=paging,
            licensee_id=licensee_id,
            license_consumer_id=license_consumer_id,
            describe_license_options=describe_license_options,
        )
        return LicenseConsumerLicensesStatus.from_api(json)

    def raise_if_consumer_unknown(
        self, license_key: Optional[str], license_consumer_id: Optional[UUID] = None
    ):
        """Raise an error is the license consumer is not provided and cannot be inferred.

        Returns if the either the license_key or license_consumer_id is set, or auth is using ID Token;
        otherwise raise error.

        Args:
            license_key: license key provided to client method
            license_consumer_id: license consumer id provided to client method.

        Raises:
            ValueError: The license consumer id is not set and there is no id token.
        """
        if license_key:
            return
        if license_consumer_id or isinstance(self.session.auth, IdTokenAuth):
            return
        raise InvalidArgumentError("license_consumer_id")

    def describe_licenses_in_use(
        self,
        licensee_id: UUID,
        license_consumer_id: Optional[UUID] = None,
        describe_license_options: Optional[DescribeLicenseOptions] = None,
        paging: Optional[PagingOptions] = None,
    ) -> LicenseConsumerClientBindingStatus:
        """Retrieve the currently checked out licenses.

        Get the list of licenses that are known to be in use by a specific license consumer (user).
        These are then returned to the client application as a list of client bindings.

        Args:
            licensee_id:
                The licensee to describe licenses for (only client bindings for licenses scoped to
                this licensee will be included in the result).
            license_consumer_id:
                The license consumer to describe licenses for. If omitted, client bindings for the
                currently logged in user are returned. Must be provided if using 10Duke ScaleJWT
                Authorization.
            describe_license_options: Options setting what information to return.
            paging: Sets limit, offset, and sorting for the result.

        Returns:
            LicenseConsumerClientBindingStatus listing the current client bindings for the
            specified license consumer.
        """
        path = "/licensing/actions/describe-license-consumer-client-bindings"
        json = _describe_request_json(
            self.session,
            self.api_url,
            path,
            paging_args=paging,
            licensee_id=licensee_id,
            license_consumer_id=license_consumer_id,
            describe_license_options=describe_license_options,
        )
        return LicenseConsumerClientBindingStatus.from_api(json)

    # pylint: disable=too-many-arguments
    def describe_license_usage(
        self,
        licensee_id: UUID,
        license_id: UUID,
        license_consumer_id: Optional[UUID] = None,
        describe_license_options: Optional[DescribeLicenseOptions] = None,
        paging: Optional[PagingOptions] = None,
    ) -> LicenseConsumerClientBindingStatus:
        """Retrieve the current usage for a license.

        Get the client bindings (existing checkouts or consumptions) of a specific license
        within a licensee.
        This provides information about what devices a license is currently checked out on and
        which license consumers (users) are using the license.

        Args:
            licensee_id:
                The licensee to describe licenses for (only client bindings for licenses scoped to
                this licensee will be included in the result).
            license_id: Identifier of the license that the information is scoped to.
            license_consumer_id:
                Optional identifier of the license consumer the the information is scoped to. Use
                only with Scale JWT authorization.
            describe_license_options: Options setting what information to return.
            paging: Sets limit, offset, and sorting for the result.

        Returns:
            LicenseConsumerClientBindingStatus listing the current client bindings for the
            specified license.
        """
        path = "/licensing/actions/describe-license-client-bindings"
        json = _describe_request_json(
            self.session,
            self.api_url,
            path,
            paging_args=paging,
            licensee_id=licensee_id,
            license_id=license_id,
            license_consumer_id=license_consumer_id,
            describe_license_options=describe_license_options,
        )

        return LicenseConsumerClientBindingStatus.from_api(json)

    def find_client_binding(
        self, licensee_id: UUID, client_binding_id: UUID, with_metadata: bool = False
    ) -> LicenseConsumerClientBindingStatus:
        """Retrieve a specific client binding.

        Get the details of a client binding, within a licensee, by its unique identifier.

        Args:
            licensee_id:
                The licensee to describe licenses for (only client bindings for licenses scoped to
                this licensee will be included in the result).
            client_binding_id: Identifier of the client binding requested.
            with_metadata:
                Flag to control including verbose information about the licenses and client
                bindings. Setting this option to true will fetch contract, order, subscription and
                external reference information at time of original license grant, the license
                container, a possible license key and related product information. For client
                bindings the additional information is related to license consumption objects and
                license consumers. Defaults to false.

        Returns:
            LicenseConsumerClientBindingStatus listing the requested client binding if found.
        """
        path = "/licensing/actions/find-license-client-binding"
        json = _describe_request_json(
            self.session,
            self.api_url,
            path,
            licensee_id=licensee_id,
            client_binding_id=client_binding_id,
            with_metadata=with_metadata,
        )

        return LicenseConsumerClientBindingStatus.from_api(json)

    def feature_flags(
        self,
        licensee_id: UUID,
        license_consumer_id: Optional[UUID] = None,
        filter_value: Optional[str] = None,
    ) -> Sequence[FeatureFlagsResponse]:
        """Retrieve licensed features that a license consumer (user) has access to.

        The list of features returned is scoped to the licensee and license consumer.

        Args:
            licensee_id:
                The licensee to describe licenses for (only licenses scoped to this licensee will
                be used to produce the result).
            license_consumer_id:
                The license consumer to describe licenses for. If omitted, licenses for the
                currently logged in user are returned. Must be provided if using 10Duke ScaleJWT
                Authorization.
            filter_value:
                Product name to match in result. Defaults to null (no filtering). The match is full
                name, case insensitive.
        """
        path = "/licensing/actions/describe-as-feature-flags"
        json = _describe_request_json(
            self.session,
            self.api_url,
            path,
            licensee_id=licensee_id,
            license_consumer_id=license_consumer_id,
            filter_value=filter_value,
        )
        flags = [FeatureFlagsResponse.from_api(item) for item in json["featureFlags"]]
        return flags

    def feature_flags_as_jwt(
        self,
        licensee_id: UUID,
        license_consumer_id: Optional[UUID] = None,
        filter_value: Optional[str] = None,
    ) -> FeatureFlagsToken:
        """Retrieve licensed features that a license consumer (user) has access to as JWT.

        The list of features returned is scoped to the licensee and license consumer.

        Args:
            licensee_id:
                The licensee to describe licenses for (only licenses scoped to this licensee will
                be used to produce the result).
            license_consumer_id:
                The license consumer to describe licenses for. If omitted, licenses for the
                currently logged in user are returned. Must be provided if using 10Duke ScaleJWT
                Authorization.
            filter_value:
                Product name to match in result. Defaults to null (no filtering). The match is full
                name, case insensitive.
        """
        path = "/licensing/actions/describe-as-feature-flags-jwt"
        jwt_text = _describe_request_text(
            self.session,
            self.api_url,
            path,
            licensee_id=licensee_id,
            license_consumer_id=license_consumer_id,
            filter_value=filter_value,
        )
        pub_key = self._jwk_client.get_signing_key_from_jwt(jwt_text)
        flags = FeatureFlagsToken(jwt_text, pub_key.key)
        return flags

    def parse_jwt(self, jwt: str) -> LicenseToken:
        """Parse JWT using public key for Scale API.

        Args:
            jwt: Raw jwt to parse.

        Returns:
            LicenseToken containing the details from the JWT.
        """
        pub_key = self._jwk_client.get_signing_key_from_jwt(jwt)
        return LicenseToken(jwt, pub_key.key)

    def describe_license_key(
        self,
        license_key: str,
        with_metadata: bool = False,
        paging: Optional[PagingOptions] = None,
    ) -> Sequence[License]:
        """Retrieve the licenses that a license key grants usage rights to.

        Args:
            license_key: The license key to get license information for.
            with_metadata:
                Flag to control including verbose information about the licenses and client
                bindings. Setting this option to true will fetch contract, order, subscription and
                external reference information at time of original license grant, the license
                container, a possible license key and related product information. For client
                bindings the additional information is related to license consumption objects and
                license consumers. Defaults to false.
            paging: Sets limit, offset, and sorting for the result.
        """
        path = "/licensing/actions/describe-license-key"
        result = _describe_request_json(
            self.session,
            self.api_url,
            path,
            license_key=license_key,
            with_metadata=with_metadata,
            paging_args=paging,
        )
        return [License.from_api(license_) for license_ in result["licenses"]]

    def describe_license_key_client_bindings(
        self,
        license_key: str,
        license_id: UUID,
        describe_license_options: Optional[DescribeLicenseOptions] = None,
        paging: Optional[PagingOptions] = None,
    ) -> LicenseConsumerClientBindingStatus:
        """Retrieve license use for a license checked out using a license key.

        Args:
            license_key: The license key to get information for.
            license_id: The license id to get checkout information for.
            describe_license_options: Options setting what information to return.
            paging: Sets limit, offset, and sorting for the result.
        """
        path = "/licensing/actions/describe-license-key-client-bindings"

        result = _describe_request_json(
            self.session,
            self.api_url,
            path,
            license_key=license_key,
            license_id=license_id,
            paging_args=paging,
            describe_license_options=describe_license_options,
        )
        return LicenseConsumerClientBindingStatus.from_api(result)

    def _start(
        self,
        action: str,
        args: Sequence[LicenseCheckoutArguments],
        license_key: Optional[str] = None,
        license_consumer_id: Optional[UUID] = None,
        client_details: Optional[ClientDetails] = None,
    ):
        self.raise_if_consumer_unknown(license_key, license_consumer_id)
        key_fragment = _license_key_fragment(license_key)
        uri = f"{self.api_url}/licensing/actions/{action}{key_fragment}"
        self._client_details = client_details or self._client_details
        headers = _concat_checkout_headers(self._client_details, license_consumer_id)
        body = [co.to_api() for co in args]
        response = self.session.post(uri, headers=headers, json=body)
        raise_for_response(response, uri)
        jwt_list = response.json()
        tokens = [self.parse_jwt(jwt) for jwt in jwt_list]
        self.store.save(tokens)
        return tokens

    def _end(
        self,
        action: str,
        args: Sequence[LicenseReleaseArguments],
        license_key: Optional[str] = None,
        license_consumer_id: Optional[UUID] = None,
        client_details: Optional[ClientDetails] = None,
    ):
        self.raise_if_consumer_unknown(license_key, license_consumer_id)
        key_fragment = _license_key_fragment(license_key)
        uri = f"{self.api_url}/licensing/actions/{action}{key_fragment}"
        self._client_details = client_details or self._client_details
        headers = _concat_checkout_headers(self._client_details, license_consumer_id)
        body = [rel.to_api() for rel in args]
        response = self.session.post(uri, headers=headers, json=body)
        raise_for_response(response, uri)
        results = response.json()
        result_models = [LicenseReleaseResult.from_api(res) for res in results]
        to_release = [
            model.released_lease_id
            for model in result_models
            if model.released and model.released_lease_id is not None
        ]
        if any(to_release):
            self.store.remove(to_release)
        return result_models

    def _raise_if_heartbeat_too_early(self, license_heartbeat_arguments):
        old_lease_ids = [arg.lease_id for arg in license_heartbeat_arguments]
        tokens = self.store.load()
        if any(
            token
            for token in tokens
            if token.lease_id in old_lease_ids
            and token.heartbeat_not_before > datetime.datetime.now(datetime.timezone.utc)
        ):
            raise HeartbeatTooEarlyError()

    def _heartbeat(
        self,
        action: str,
        args: Sequence[LicenseHeartbeatArguments],
        license_key: Optional[str] = None,
        license_consumer_id: Optional[UUID] = None,
        client_details: Optional[ClientDetails] = None,
    ) -> Sequence[LicenseToken]:
        self.raise_if_consumer_unknown(license_key, license_consumer_id)
        self._raise_if_heartbeat_too_early(args)
        key_fragment = _license_key_fragment(license_key)
        uri = f"{self.api_url}/licensing/actions/{action}{key_fragment}"
        self._client_details = client_details or self._client_details
        headers = _concat_checkout_headers(self._client_details, license_consumer_id)
        body = [args.to_api() for args in args]
        response = self.session.post(uri, json=body, headers=headers)
        raise_for_response(response, uri)
        jwt_list = response.json()
        tokens = [self.parse_jwt(jwt) for jwt in jwt_list]
        self.store.update(tokens)
        return tokens
