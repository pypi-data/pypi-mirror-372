import os
from typing import Dict, Optional, TypedDict

import aiobotocore.client
import httpx

from ts_sdk_connectors_python.aws import AWS
from ts_sdk_connectors_python.certificate import CertConfig, create_combined_ssl_context
from ts_sdk_connectors_python.constants import DEFAULT_HTTPX_TIMEOUT_SECONDS, EnvVars
from ts_sdk_connectors_python.logger import get_logger
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client import (
    AuthenticatedClient,
)


def is_standalone() -> bool:
    """
    Returns True if the CONNECTOR_TOKEN environment variable is set, otherwise returns False
    """
    return os.getenv(EnvVars.CONNECTOR_TOKEN) is not None


class SSMParameter(TypedDict):
    """Represents the SSM Parameter inside a SSM GetParameter response."""

    Name: str
    Type: str
    Value: str
    Version: int
    LastModifiedDate: str
    ARN: str


class SSMGetParameterResponse(TypedDict):
    """Represents the response from the AWS SSM GetParameter API."""

    Parameter: SSMParameter


async def get_parameter_value(
    ssm_parameter_name: str, ssm_client: aiobotocore.client.AioBaseClient
) -> str:
    """
    Fetches a parameter from the AWS SSM Parameter Store by name and returns the decrypted value.
    """
    response: SSMGetParameterResponse = await ssm_client.get_parameter(
        Name=ssm_parameter_name, WithDecryption=True
    )
    value = response["Parameter"]["Value"]
    return value


class AuthenticatedClientCreator:
    def __init__(
        self,
        base_url: str = "https://example.com",
        cert_config: Optional[CertConfig] = None,
        disable_verify: bool = False,
        proxy: Optional[str] = None,
        proxies: Optional[Dict[str, str]] = None,
        timeout: int | float | None = DEFAULT_HTTPX_TIMEOUT_SECONDS,
        aws: Optional[AWS] = None,
    ):
        """
        Initializes the configuration for the AuthenticatedClientCreator.

        :param base_url: The base URL for the API client.
        :param cert_config: SSL certificate configuration.
        :param disable_verify: Flag to disable SSL verification. If set to True, cert_config will be ignored.
        :param proxy: A single proxy URL to use.
        :param proxies: Multiple proxy URLs for different schemes (http, https).
        :param timeout: Httpx client timeout. Defaults to `DEFAULT_HTTPX_TIMEOUT`.
        :param aws: An AWS object used to interact with AWS services.
        """
        # TODO: rename internal variables to match the naming convention
        self.base_url = base_url
        self.cert_config = cert_config
        self.disable_verify = disable_verify
        self.proxy = proxy
        self.proxies = proxies
        self.verify = not disable_verify  # can be one of -- True, False, or SSL Context
        self.logger = get_logger(__class__.__name__)
        self.sync_proxy_mounts = None
        self.async_proxy_mounts = None
        self.timeout = timeout
        self.aws = aws if aws else AWS(connector_id="", org_slug="")

        if proxy and proxies:
            raise ValueError(
                "You can only provide one of `proxy` or `proxies`, not both."
            )

        self.set_proxies(proxies)

    async def set_ssl_verification(
        self, cert_config: Optional[CertConfig], disable_verify: bool
    ):
        """
        Configures SSL verification based on the provided cert_config and disable_verify flag.
        """
        if disable_verify:
            if cert_config:
                self.logger.warning(
                    "disable_verify is set to True, ignoring cert_config"
                )
            return False

        if cert_config:
            return await create_combined_ssl_context(self.aws, self.logger, cert_config)

        return True

    def set_proxies(self, proxies: Optional[Dict[str, str]]) -> None:
        """
        Configures proxies for the client based on the provided proxies dictionary.
        """
        if proxies:
            self.sync_proxy_mounts = {
                scheme: httpx.HTTPTransport(proxy=proxy_url)
                for scheme, proxy_url in proxies.items()
            }
            self.async_proxy_mounts = {
                scheme: httpx.AsyncHTTPTransport(proxy=proxy_url)
                for scheme, proxy_url in proxies.items()
            }

    async def get_auth_token(self) -> str:
        """
        Provides the auth token to communicate with TDP.
        """
        user_provided_token = os.getenv(EnvVars.CONNECTOR_TOKEN)
        ssm_parameter_name = os.getenv(EnvVars.JWT_TOKEN_PARAMETER)
        if user_provided_token:
            return user_provided_token

        if not ssm_parameter_name:
            raise ValueError(
                f"Unable to retrieve an auth token because {EnvVars.CONNECTOR_TOKEN} and {EnvVars.JWT_TOKEN_PARAMETER} do not exist."
            )

        async with await self.aws.create_client("ssm") as ssm_client:
            return await get_parameter_value(ssm_parameter_name, ssm_client=ssm_client)

    def _log_request(self, request):
        self.logger.debug(f"Request: {request.method} {request.url}")
        safe_headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in ("authorization", "ts-auth-token")
        }
        self.logger.debug(f"Request headers: {safe_headers}")

    def _log_response(self, response):
        request = response.request
        self.logger.debug(
            f"Response: {request.method} {request.url} - Status {response.status_code}"
        )
        self.logger.debug(f"Response headers: {dict(response.headers)}")

    async def _async_log_request(self, request):
        self._log_request(request)

    async def _async_log_response(self, response):
        self._log_response(response)

    async def create(self) -> AuthenticatedClient:
        """
        Creates and returns an `AuthenticatedClient` with the provided configuration.
        """
        token = await self.get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}

        self.verify = await self.set_ssl_verification(
            self.cert_config, self.disable_verify
        )

        client = AuthenticatedClient(base_url=self.base_url, token=token)

        if self.timeout:
            client._timeout = httpx.Timeout(self.timeout)
        httpx_timeout = client._timeout

        async_client = httpx.AsyncClient(
            base_url=self.base_url,
            proxy=self.proxy,
            mounts=self.async_proxy_mounts,
            verify=self.verify,
            headers=headers,
            timeout=httpx_timeout,
            event_hooks={
                "request": [self._async_log_request],
                "response": [self._async_log_response],
            },
        )

        sync_client = httpx.Client(
            base_url=self.base_url,
            proxy=self.proxy,
            mounts=self.sync_proxy_mounts,
            verify=self.verify,
            headers=headers,
            timeout=httpx_timeout,
            event_hooks={
                "request": [self._log_request],
                "response": [self._log_response],
            },
        )
        client.set_async_httpx_client(async_client)
        client.set_httpx_client(sync_client)

        return client
