import functools
import os
from typing import Awaitable, Callable, TypeAlias, TypedDict

import aioboto3
import aiobotocore
import aiobotocore.credentials
import aiobotocore.session

from ts_sdk_connectors_python.constants import EnvVars
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.api.connectors import (
    connector_controller_get_credentials,
)
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.client import (
    AuthenticatedClient,
)

AwsClientContextManager: TypeAlias = (
    aiobotocore.session.ClientCreatorContext
)  # the async context manager which generates an aiobotocore.client.AioBaseClient


class AwsCredentials(TypedDict):
    """A container for the AWS credentials provided to aiobotocore"""

    access_key: str
    secret_key: str
    token: str
    expiry_time: str


class TdpAsyncRefreshableCredentials(aiobotocore.credentials.AioRefreshableCredentials):
    """Custom AioRefreshableCredentials for TDP"""


class RefreshableTdpCredentialsProvider(aiobotocore.credentials.AioConfigProvider):
    """
    This class is used by aiobotocore to load and refresh credentials from TDP.
    """

    METHOD = "TDP GetConnectorCredentials"
    CANONICAL_NAME = "custom-tdp-credentials-provider"

    def __init__(
        self, refresh_callback: Callable[[], Awaitable[AwsCredentials]]
    ) -> None:
        self.refresh_callback = refresh_callback

    async def load(self) -> TdpAsyncRefreshableCredentials:
        """
        This method is called by aiobotocore to load credentials.
        """
        credentials = await self.refresh_callback()
        refreshable = TdpAsyncRefreshableCredentials.create_from_metadata(
            metadata=credentials,
            refresh_using=self.refresh_callback,
            method=self.METHOD,
        )
        return refreshable


class AWS:
    """
    This class centralizes the logic for creating AWS clients. It adds support for standalone
    deployment and retrieves short-lived credentials from the company endpoint if needed.
    """

    def __init__(
        self,
        connector_id: str | None,
        org_slug: str | None,
        http_client: AuthenticatedClient | None = None,
        aws_region: str | None = None,
        logger=None,
    ) -> None:
        """
        Initializes the AWS class with necessary parameters.
        """
        self.http_client = http_client
        self.connector_id = connector_id
        self.org_slug = org_slug
        self.connector_token = os.getenv(EnvVars.CONNECTOR_TOKEN)
        self.aws_region = (
            aws_region if aws_region else os.environ.get(EnvVars.AWS_REGION)
        )
        self.logger = logger

        if not self.aws_region:
            raise RuntimeError(
                "AWS Region is required to connect to AWS. Provide as an argument or set the AWS_REGION environment variable."
            )

        # This if-else block applies RefreshableTdpCredentialsProvider to the AWS session when HTTP communication with TDP is possible
        # IDEA: this block can be potentially removed if RefreshableTdpCredentialsProvider.load returns None in a non-Standalone context.
        # This would allow Aiobotocore to skip the RefreshableTdpCredentialsProvider and proceed down the
        # credentials provider chain: env > assume-role > assume-role-with-web-identity > sso > etc
        if http_client and connector_id and org_slug and self.connector_token:
            self.session = self._get_session(
                connector_id=connector_id, org_slug=org_slug
            )
        else:
            self.session = aioboto3.Session()

    async def create_client(
        self,
        service_name: str,
    ) -> AwsClientContextManager:
        """
        Returns an async context manager for creating aiobotocore clients like 's3', 'sqs', 'ssm', or 'logs'

        Args:TDP Credentials data
            service_name (str): The AWS service name
            session_kwargs: Additional arguments to pass to the aiobotocore session

        Usage:

        async with aws.create_client("s3") as client:
            response = await client.get_object(Bucket="my-bucket", Key="my-key")

        """
        return self.session.client(
            service_name=service_name, region_name=self.aws_region
        )

    async def _get_credentials_from_tdp(
        self,
        client: AuthenticatedClient,
        connector_id: str | None = None,
        org_slug: str | None = None,
    ) -> AwsCredentials:
        """Fetches credentials from TDP and formats them for aiobotocore"""

        if not client:
            raise RuntimeError("Unable to get AWS credentials without a HTTP Client")
        if not connector_id:
            raise RuntimeError("Unable to get AWS credentials without a Connector ID")
        if not org_slug:
            raise RuntimeError(
                "Unable to get AWS credentials without an Organization Slug"
            )
        if not self.logger:
            raise RuntimeError("Unable to get AWS credentials without a logger")

        response = await connector_controller_get_credentials.asyncio_detailed(
            id=connector_id, client=client, x_org_slug=org_slug
        )

        data = response.parsed
        ts_request_id = response.headers.get("ts-request-id")

        if not data or response.status_code != 200:
            message = f"Unable to get AWS credentials from TDP due to {response.status_code} status code. {ts_request_id=}"
            self.logger.error(
                message,
                extra={
                    "ts-request-id": ts_request_id,
                    "status_code": response.status_code,
                },
            )
            raise RuntimeError(message)

        self.logger.debug(
            f"AWS credentials retrieved from TDP",
            extra={"ts-request-id": ts_request_id, "expiry_time": data.expiration_date},
        )

        credentials: AwsCredentials = {
            "access_key": data.access_key_id,
            "secret_key": data.secret_access_key,
            "token": data.session_token,
            "expiry_time": data.expiration_date,
        }

        return credentials

    def _get_session(
        self, connector_id: str, org_slug: str, **kwargs
    ) -> aioboto3.Session:
        """
        Return an aiobotocore.session.AioSession that can establish/refresh authentication
        with the TetraScience AWS Account.

        The session features a credentials provider that polls the TDP v1/connector/{id}/credentials
        endpoint for new credentials when the current ones expire.
        """

        if not self.http_client:
            raise RuntimeError("Unable to initiate AWS session without a HTTP Client")
        if not self.connector_id:
            raise RuntimeError(
                "Unable to fetch connector AWS session credentials without Connector ID"
            )
        if not self.org_slug:
            raise RuntimeError(
                "Unable to fetch conenctor AWS session credentials without an org slug"
            )

        # the aiobotocore library lets us create a session with a custom credential provider
        aio_session = aiobotocore.session.AioSession(**kwargs)
        get_connector_credentials = functools.partial(
            self._get_credentials_from_tdp,
            client=self.http_client,
            connector_id=connector_id,
            org_slug=org_slug,
        )
        tdp_credential_provider = RefreshableTdpCredentialsProvider(
            refresh_callback=get_connector_credentials
        )

        resolver = aio_session.get_component("credential_provider")
        first_provider = resolver.providers[0]
        resolver.insert_before(first_provider.METHOD, tdp_credential_provider)

        # aioboto3 session is used to create aioboto3 clients, which have higher level APIs than aiobotocore clients
        session = aioboto3.Session(botocore_session=aio_session)
        return session
