import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Protocol, Self, Type, TypeVar, Union

from ts_sdk_connectors_python import CloudWatchLoggingAdapter
from ts_sdk_connectors_python.aws import AWS
from ts_sdk_connectors_python.aws_factory import AWSFactory
from ts_sdk_connectors_python.certificate import CertConfig
from ts_sdk_connectors_python.client_creator import AuthenticatedClientCreator
from ts_sdk_connectors_python.config import TdpApiConfig
from ts_sdk_connectors_python.constants import HUB_PROXY_PATH
from ts_sdk_connectors_python.file_uploader import UploadFileRequest
from ts_sdk_connectors_python.logger import get_logger
from ts_sdk_connectors_python.logger._buffer import EarlyLogBuffer
from ts_sdk_connectors_python.logger._cloudwatch import CloudWatchLoggingManager
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client import (
    AuthenticatedClient,
    Client,
)
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.models import (
    ConnectorDetailsDto,
    UpdateConnectorHealthRequest,
)
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.types import (
    Response,
)


class FromDictProtocol(Protocol):
    @classmethod
    def from_dict(cls: Type[Self], src_dict: dict) -> Self:
        ...  # Ellipsis indicates interface-only


T = TypeVar("T", bound=FromDictProtocol)


class TdpApiError(Exception):
    """
    Generic exception for TdpApi

    Attributes:
        ts_request_id: The TDP request ID associated with the error, if available
    """

    def __init__(self, message: str, ts_request_id: Optional[str] = None):
        """
        Initialize a TdpApiError

        Args:
            message: The error message
            ts_request_id: The TDP request ID associated with the error, if available
        """
        self.ts_request_id = ts_request_id
        if ts_request_id:
            message = f"{message} (ts-request-id: {ts_request_id})"
        else:
            message = f"{message} (ts-request-id: N/A)"
        super().__init__(message)


class _TdpApiBase(ABC):
    def __init__(
        self,
        client: Optional[AuthenticatedClient | Client] = None,
        config: Optional[TdpApiConfig] = None,
    ):
        self.config = config or TdpApiConfig()
        self._client = client
        self._aws = None
        self._aws_factory = AWSFactory()
        log_extra = {
            "orgSlug": self.config.org_slug,
            "connectorId": self.config.connector_id,
            "hubId": self.config.hub_id,
        }
        log_extra = {k: v for k, v in log_extra.items() if v is not None}
        self._logger = get_logger(
            __name__, extra=log_extra
        )  # logger is not initialized here

        # Load proxy settings from the Hub or environment
        self.load_proxy_settings_to_env()

    @property
    def logger(self) -> CloudWatchLoggingAdapter:
        return self._logger

    @property
    def org_slug(self) -> str:
        """
        Returns the org_slug set in the configuration
        """
        org_slug = self.config.org_slug
        if org_slug is None:
            raise TdpApiError("orgSlug is required to be set")
        return org_slug

    @property
    def aws(self) -> AWS:
        """
        Returns the AWS client used for communicating with AWS services
        """
        if self._aws is None:
            raise TdpApiError("AWS client is not initialized")
        return self._aws

    @property
    def client(self) -> AuthenticatedClient:
        """
        Returns the AuthenticatedClient used for communicating with TDP

        Raises:
            TdpApiError: Raised when the client is not yet initialized
        """
        if self._client is None:
            raise TdpApiError(
                f"client is not initialized. Provide a client on initialization or use {self.init_client.__name__}"
                f" to initialize client."
            )
        return self._client

    def update_headers(self, additional_headers: dict[str, str]):
        """
        Update headers to the initialized httpx clients. This will perform
        `headers.update(additional_headers)`, meaning it is not possible to remove headers
        using this method.

        :param additional_headers: Headers to update.
        :return:
        """
        self.logger.info(f"Updating headers: {additional_headers}")
        sync_client = self.client.get_httpx_client()
        async_client = self.client.get_async_httpx_client()
        self.client._headers.update(additional_headers)
        async_client.headers.update(additional_headers)
        sync_client.headers.update(additional_headers)

    def _convert_dict_to_model(self, data_dict: dict, model_class: Type[T]) -> T:
        """
        Convert a dictionary to a model object

        Args:
            data_dict: Dictionary containing model data
            model_class: Class with from_dict method to convert dictionary to object

        Returns:
            Instance of model_class created from data_dict

        Raises:
            TdpApiError: If conversion fails due to invalid data or missing attributes
        """
        try:
            if not hasattr(model_class, "from_dict"):
                error_msg = f"Model class {model_class.__name__} lacks from_dict method"
                self._logger.error(error_msg)
                raise TypeError(error_msg)

            if not isinstance(data_dict, dict):
                error_msg = f"Expected dictionary, got {type(data_dict).__name__}"
                self._logger.error(error_msg)
                raise TypeError(error_msg)

            return model_class.from_dict(data_dict)
        except Exception as e:
            model_name = getattr(model_class, "__name__", "Unknown")
            error_msg = f"Failed to convert dict to {model_name} model: {e}"
            self._logger.error(error_msg, exc_info=True)
            raise TdpApiError(error_msg) from e

    def client_is_initialized(self) -> bool:
        """
        Returns True if the client has been initialized
        """
        return self._client is not None

    def load_proxy_settings_to_env(self) -> None:
        """
        Loads proxy settings from the Hub and promotes them to environment variables.
        Both httpx and aiohttp check for these env vars

        If the Hub proxy file doesn't exist, it will check if uppercase environment
        variables are already set.
        """
        self.logger.info("Loading proxy settings from Hub")
        try:
            # Check if the file exists and is readable
            proxy_path = Path(HUB_PROXY_PATH)
            if proxy_path.exists() and os.access(proxy_path, os.R_OK):
                # Parse the proxy environment file
                with open(proxy_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()

                            # Remove quotes if present
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]

                            # Set uppercase environment variables based on lowercase ones
                            if key in ["http_proxy", "HTTP_PROXY"]:
                                os.environ["HTTP_PROXY"] = value
                                self.logger.info(
                                    f"Set HTTP_PROXY from Hub proxy file: {value}"
                                )
                            elif key in ["https_proxy", "HTTPS_PROXY"]:
                                os.environ["HTTPS_PROXY"] = value
                                self.logger.info(
                                    f"Set HTTPS_PROXY from Hub proxy file: {value}"
                                )
                            elif key in ["no_proxy", "NO_PROXY"]:
                                os.environ["NO_PROXY"] = value
                                self.logger.info(
                                    f"Set NO_PROXY from Hub proxy file: {value}"
                                )

                self.logger.info(
                    "Loaded proxy settings from Hub",
                    extra={
                        "isNoProxySet": "NO_PROXY" in os.environ,
                        "isHttpProxySet": "HTTP_PROXY" in os.environ,
                        "isHttpsProxySet": "HTTPS_PROXY" in os.environ,
                    },
                )
            else:
                self.logger.info(
                    "No Hub env proxy file found", {"hubProxyPath": HUB_PROXY_PATH}
                )

                # If lowercase environment variables exist but uppercase ones don't,
                # copy the lowercase values to uppercase
                if "no_proxy" in os.environ and "NO_PROXY" not in os.environ:
                    os.environ["NO_PROXY"] = os.environ["no_proxy"]
                    self.logger.info("Set NO_PROXY from no_proxy")

                if "http_proxy" in os.environ and "HTTP_PROXY" not in os.environ:
                    os.environ["HTTP_PROXY"] = os.environ["http_proxy"]
                    self.logger.info("Set HTTP_PROXY from http_proxy")

                if "https_proxy" in os.environ and "HTTPS_PROXY" not in os.environ:
                    os.environ["HTTPS_PROXY"] = os.environ["https_proxy"]
                    self.logger.info("Set HTTPS_PROXY from https_proxy")

                self.logger.info(
                    "Environment proxy settings",
                    {
                        "isNoProxySet": "NO_PROXY" in os.environ,
                        "isHttpProxySet": "HTTP_PROXY" in os.environ,
                        "isHttpsProxySet": "HTTPS_PROXY" in os.environ,
                    },
                )
        except Exception as e:
            self.logger.error("Error reading proxy env file", exc_info=True)
            raise TdpApiError(f"Error reading proxy env file: {e}") from e

    async def init_client(
        self, proxy_url: Optional[str] = None, disable_verify: bool = False
    ) -> Self:
        """
        Initializes and sets the AWS and HTTP clients for communicating with TDP and connector AWS services
        """
        if self.config.connector_token:
            await self.__init_standalone_env(
                token=self.config.connector_token,
                proxy_url=proxy_url,
                disable_verify=disable_verify,
            )
        else:
            await self.__init_tetra_env(
                proxy_url=proxy_url, disable_verify=disable_verify
            )

        if (
            self.config.connector_token
            and bool(self.config.skip_cloudwatch) is not True
        ):
            # these will be set in runtime because the init methods above have completed.
            assert (
                self._aws is not None
            ), "aws is required for CloudWatch logger initialization"
            assert (
                self.config.connector_id is not None
            ), "connector_id is required for CloudWatch logger initialization"
            assert (
                self.config.org_slug is not None
            ), "org_slug is required for CloudWatch logger initialization"

            self._logger.info("Initializing CloudWatch logger  ~~~~~~~")
            await CloudWatchLoggingManager.init_reporter(
                connector_id=self.config.connector_id,
                tdp_api=self,
                org_slug=self.config.org_slug,
                aws_factory=self._aws_factory,
            )
            self._logger.info("Cloudwatch logger initialized")

            # Flush early logs to CloudWatch
            self._flush_early_logs_to_cloudwatch()
        self._logger.info("Client initialized")
        return self

    def _flush_early_logs_to_cloudwatch(self):
        """Flush early buffered logs to CloudWatch"""
        try:
            buffered_count = EarlyLogBuffer.get_buffered_count()
            if buffered_count > 0:
                # These should be set by the time CloudWatch is initialized
                assert (
                    self.config.connector_id is not None
                ), "connector_id is required for early log buffer flush to CloudWatch"
                assert (
                    self.config.org_slug is not None
                ), "org_slug is required for early log buffer flush to CloudWatch"

                self._logger.info(f"Flushing {buffered_count} early logs to CloudWatch")
                EarlyLogBuffer.flush_to_cloudwatch(
                    connector_id=self.config.connector_id, org_slug=self.config.org_slug
                )
                self._logger.info("Early logs flushed to CloudWatch")
            else:
                self._logger.debug("No early logs to flush")
        except Exception as e:
            self._logger.warning(f"Failed to flush early logs to CloudWatch: {e}")

    async def __init_tetra_env(
        self, proxy_url: Optional[str] = None, disable_verify: bool = False
    ) -> None:
        """
        Connectors deployed in a "Tetra-hosted" environment (e.g. Cloud deployed or on a Hub)
        """
        self._logger.info("Initializing in non-standalone environment")
        if not self.config.tdp_endpoint:
            raise TdpApiError("TdpApi endpoint is not set")
        if not self.config.connector_id:
            raise TdpApiError("TdpApi connector ID is not set")
        if not self.config.org_slug:
            raise TdpApiError("TdpApi org-slug is not set")

        cert_config = CertConfig(
            local_cert_file=self.config.local_certificate_file,
            stream_bucket=self.config.stream_bucket,
            tdp_certificate_key=self.config.tdp_certificate_key,
        )

        # This HTTP Client should retrieve the connector auth token from AWS and use it for all requests
        self._logger.info("Creating HTTP client for communicating with TDP")
        client = await AuthenticatedClientCreator(
            base_url=self.config.tdp_endpoint,
            cert_config=cert_config,
            proxy=proxy_url,
            disable_verify=disable_verify,
        ).create()

        self._logger.info("Creating AWS client for connector AWS services")
        aws = await self._aws_factory.get_aws_instance(
            connector_id=self.config.connector_id,
            org_slug=self.config.org_slug,
            http_client=client,
            aws_region=self.config.aws_region,
        )

        self._client = client
        self._aws = aws

    async def __init_standalone_env(
        self,
        token: str,
        proxy_url: Optional[str] = None,
        disable_verify: bool = False,
    ) -> None:
        """
        Connectors is deployed in a "Standalone" environment
        """
        self._logger.info("Initializing a standalone deployment")
        if not self.config.tdp_endpoint:
            raise TdpApiError("TdpApi endpoint is not set")
        if not self.config.connector_id:
            raise TdpApiError("TdpApi Connector ID is not set")
        if not self.config.org_slug:
            raise TdpApiError("TdpApi org-slug is not set")

        cert_config = CertConfig(
            local_cert_file=self.config.local_certificate_file,
            stream_bucket=self.config.stream_bucket,
            tdp_certificate_key=self.config.tdp_certificate_key,
        )

        self._logger.info("Creating AWS client for connector AWS services")
        # create a single-use http client for AWS Credential refresh logic.
        # This bootstaps the AWS sessions for communicating with SQS, S3, SSM, etc.
        _client = await AuthenticatedClientCreator(
            base_url=self.config.tdp_endpoint,
            cert_config=cert_config,
            proxy=proxy_url,
            disable_verify=disable_verify,
            aws=None,
        ).create()

        # Use the factory to get an AWS instance
        aws = await self._aws_factory.get_aws_instance(
            connector_id=self.config.connector_id,
            org_slug=self.config.org_slug,
            http_client=_client,
            aws_region=self.config.aws_region,
        )

        self._logger.info("Creating HTTP client for communicating with TDP")
        # This HTTP client creator does not need to retrieve the connector token from AWS
        client = await AuthenticatedClientCreator(
            base_url=self.config.tdp_endpoint,
            cert_config=cert_config,
            proxy=proxy_url,
            disable_verify=disable_verify,
            aws=None,
        ).create()

        self._client = client
        self._aws = aws

    @abstractmethod
    def upload_file(
        self,
        request: UploadFileRequest,
        connector_details: Optional[ConnectorDetailsDto],
        strict_mtl_validation: bool = False,
    ):
        pass

    @abstractmethod
    def update_health(
        self,
        connector_id: str,
        update_connector_health_request: Union[UpdateConnectorHealthRequest, dict],
        version: Optional[str] = "v1",
    ) -> Response[Any]:
        pass

    async def _stop_cloudwatch(self):
        self.logger.info("Stopping CloudWatch logger")
        # These should be set if CloudWatch was initialized
        assert (
            self.config.connector_id is not None
        ), "connector_id is required for CloudWatch stop"
        assert (
            self.config.org_slug is not None
        ), "org_slug is required for CloudWatch stop"
        await CloudWatchLoggingManager.stop_cloudwatch(
            connector_id=self.config.connector_id, org_slug=self.config.org_slug
        )

    def set_tdp_api_client_raise_on_unexpected_status(
        self, enabled: bool = True
    ) -> Self:
        """
        Configure whether the TDP API client should raise exceptions for unexpected HTTP status codes.

        When enabled, the client will raise an UnexpectedStatus exception if the API returns
        a status code that wasn't explicitly documented in the OpenAPI specification.
        This is useful for debugging and ensures that unexpected responses are properly handled.

        Note: This only affects the HTTP or HTTPX client used for TDP API calls, not the AWS client.

        Args:
            enabled: Whether to enable raising exceptions for unexpected status codes

        Returns:
            Self for method chaining

        Raises:
            TdpApiError: If the client is not initialized
        """
        self.client.raise_on_unexpected_status = enabled
        return self
