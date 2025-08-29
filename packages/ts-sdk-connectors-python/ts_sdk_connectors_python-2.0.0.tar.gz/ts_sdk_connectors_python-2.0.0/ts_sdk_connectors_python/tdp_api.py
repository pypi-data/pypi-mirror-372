import inspect
import ssl
from typing import Any, Callable, Dict, List, Optional, Union

import certifi
import httpx

from ts_sdk_connectors_python.file_uploader import (
    FileUploader,
    UploadFileRequest,
    UploadFileResponse,
)
from ts_sdk_connectors_python.logger import get_logger
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.api.connectors import (
    connector_controller_get_by_id,
    connector_controller_get_config,
    connector_controller_get_data,
    connector_controller_get_files,
    connector_controller_heartbeat,
    connector_controller_report_metrics,
    connector_controller_save_data,
    connector_controller_update_files,
    connector_controller_update_health,
)
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.models import (
    ConnectorDataResponse,
    ConnectorDetailsDto,
    ConnectorFilesResponse,
    ReportMetricsRequest,
    SaveConnectorDataRequest,
    SaveConnectorFilesRequest,
    SaveConnectorFilesResponse,
    UpdateConnectorHealthRequest,
)
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.types import (
    UNSET,
    Response,
    Unset,
)
from ts_sdk_connectors_python.tdp_api_base import TdpApiError, _TdpApiBase
from ts_sdk_connectors_python.tdp_api_models import CertificateDto
from ts_sdk_connectors_python.utils import extract_request_id

logger = get_logger(__name__)


class TdpApi(_TdpApiBase):
    """
    This class exposes methods to interact with the Tetra Data Platform REST API

    All methods are asynchronous (use async/await)
    """

    async def _call_with_error_handling(self, func: Callable):
        """Execute a function with error handling for async operations"""
        try:
            result = func()
            if inspect.isawaitable(result):
                return await result
            return result
        except (ValueError, TypeError) as e:
            self.logger.error(f"{e.__class__.__name__}: {e}", exc_info=True)
            raise  # Re-raise these errors directly without wrapping
        except Exception as e:
            ts_request_id = extract_request_id(e)

            log_extra = {"ts-request-id": ts_request_id} if ts_request_id else {}
            self.logger.error(f"API call failed: {e}", exc_info=True, extra=log_extra)

            raise TdpApiError(
                f"API call failed: {e}", ts_request_id=ts_request_id
            ) from e

    async def get_connector_by_id(
        self,
        connector_id: str,
        resolve_secrets: Optional[bool] = None,
        version: Optional[str] = "v1",
        include: Union[Unset, list[str]] = UNSET,
    ) -> Response[ConnectorDetailsDto]:
        """
        Get connector object by ID
        GET /v1/data-acquisition/connectors/{id}
        """
        api_version_map = {
            "v1": connector_controller_get_by_id.asyncio_detailed,
            # Add other versions here if needed
        }

        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                client=self.client,
                x_org_slug=self.org_slug,
                id=connector_id,
                resolve_secrets=resolve_secrets,
                include=include,
            )
            return await self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    async def get_connector_config(
        self,
        connector_id: str,
        connector_version: Optional[str] = "",
        version: Optional[str] = "v1",
    ) -> Response[Any]:
        """
        Gets connector config
        GET `/v1/data-acquisition/connectors/${id}/config/${query?.version}`
        """
        api_version_map = {
            "v1": connector_controller_get_config.asyncio_detailed,
            # Add other versions here if needed
        }

        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                client=self.client,
                id=connector_id,
                version=connector_version,
                x_org_slug=self.org_slug,
            )
            return await self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    # TODO: add use_object_notation support
    async def get_connector_data(
        self,
        connector_id: str,
        keys: Union[Unset, str] = UNSET,
        version: Optional[str] = "v1",
    ) -> Response[ConnectorDataResponse]:
        """
        Gets connector data from the key-value store
        GET /v1/connectors/{id}/data

        :param connector_id: The ID of the connector
        :param keys: Optional comma-separated list of keys to filter the results
        :param version: API version to use
        :return: Response containing connector data
        """
        api_version_map = {
            "v1": connector_controller_get_data.asyncio_detailed,
            # Add other versions here if needed
        }

        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                client=self.client,
                id=connector_id,
                keys=keys,
                x_org_slug=self.org_slug,
            )
            return await self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    async def save_connector_data(
        self,
        connector_id: str,
        raw_data: Union[SaveConnectorDataRequest, dict, List[dict]],
        version: Optional[str] = "v1",
    ) -> Response[ConnectorDataResponse]:
        """
        Saves connector data in the key-value store
        PUT /v1/connectors/{id}/data

        Args:
            connector_id: The ID of the connector.
            raw_data: Data values to save. Can be one of:
                - A SaveConnectorDataRequest object
                - A dictionary with "values" key containing a list of data items
                - A list of data dictionaries (will be auto-wrapped with "values" key)

                Each data item should include fields like:
                - key: The data key name
                - value: The value to store
                - secure: Whether the value should be stored securely
            version: The API version to use. Defaults to "v1".

        Returns:
            Response containing the saved connector data.
        """
        api_version_map = {
            "v1": connector_controller_save_data.asyncio_detailed,
            # Add other versions here if needed
        }

        # Convert various input formats to SaveConnectorDataRequest
        if isinstance(raw_data, list):
            # Auto-wrap list of data items with "values" key
            raw_data = {"values": raw_data}

        # Convert dict to SaveConnectorDataRequest if needed
        if isinstance(raw_data, dict):
            body = self._convert_dict_to_model(raw_data, SaveConnectorDataRequest)
        else:
            # Already a SaveConnectorDataRequest object
            body = raw_data

        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                client=self.client,
                id=connector_id,
                x_org_slug=self.org_slug,
                body=body,
            )
            return await self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    async def get_connector_files(
        self,
        connector_id: str,
        get_connector_files_query_params={},
        version: Optional[str] = "v1",
    ) -> Response[ConnectorFilesResponse]:
        """
        Retrieves files uploaded by a connector.

        Args:
            connector_id: The ID of the connector.
            get_connector_files_query_params: Query parameters for filtering and sorting the files.
                - file_ids: List of file IDs to include.
                - exclude_file_ids: List of file IDs to exclude.
                - unique_external_ids: List of unique external IDs to include.
                - exclude_unique_external_ids: List of unique external IDs to exclude.
                - statuses: List of processing statuses to include.
                - max_errors: Maximum number of errors allowed.
                - created_before: Include files created before this date.
                - created_after: Include files created after this date.
                - updated_before: Include files updated before this date.
                - updated_after: Include files updated after this date.
                - order_by: Field to order the results by.
                - order_direction: Direction to order the results ('ASC' or 'DESC').
                - take: Number of records to take.
                - skip: Number of records to skip.
            version: The API version to use. async defaults to "v1".

        Raises:
            ValueError: If the API version is unsupported.

        Returns:
            The response from the API.
        """
        api_version_map = {
            "v1": connector_controller_get_files.asyncio_detailed,
            # Add other versions here when available
        }
        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                client=self.client,
                id=connector_id,
                x_org_slug=self.org_slug,
                **get_connector_files_query_params,
            )
            return await self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    async def update_connector_files(
        self,
        connector_id: str,
        files_data: Union[SaveConnectorFilesRequest, dict, List[dict]],
        version: Optional[str] = "v1",
    ) -> Response[SaveConnectorFilesResponse]:
        """
        Updates files associated with a connector.

        Args:
            connector_id: The ID of the connector.
            files_data: Files data to update. Can be one of:
                - A SaveConnectorFilesRequest object
                - A dictionary with "files" key containing a list of file objects
                - A list of file dictionaries (will be auto-wrapped with "files" key)

                Each file object should include information like:
                - id: The file ID.
                - uniqueExternalId: The unique external ID.
                - metadata: Metadata associated with the file.
                - status: The processing status of the file.
                - filepath: The file path.
                - errorCount: The number of errors.
                - errorMessage: The error message.
            version: The API version to use. Defaults to "v1".

        Raises:
            ValueError: If the API version is unsupported.

        Returns:
            The response from the API.
        """
        api_version_map = {
            "v1": connector_controller_update_files.asyncio_detailed,
            # Add other versions here when available
        }

        # Convert various input formats to SaveConnectorFilesRequest
        if isinstance(files_data, list):
            # Auto-wrap list of file dictionaries with "files" key
            files_data = {"files": files_data}

        # Convert dict to SaveConnectorFilesRequest
        if isinstance(files_data, dict):
            files_data = self._convert_dict_to_model(
                files_data, SaveConnectorFilesRequest
            )

        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                client=self.client,
                id=connector_id,
                x_org_slug=self.org_slug,
                body=files_data,
            )
            return await self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    async def report_metrics(
        self,
        connector_id: str,
        metrics: Union[ReportMetricsRequest, dict, List[dict]],
        version: Optional[str] = "v1",
    ) -> Response[Any]:
        """
        Reports metrics to the Tetra Data Platform.

        Args:
            connector_id: The ID of the connector.
            metrics: The metrics to report. Can be one of:
                - A ReportMetricsRequest object
                - A dictionary with a "metrics" key containing a list of metric objects
                - A list of metric objects (will be auto-wrapped with "metrics" key)
            version: The API version to use. Defaults to "v1".

        Raises:
            ValueError: If the API version is unsupported.

        Returns:
            The response from the API.
        """
        api_version_map = {
            "v1": connector_controller_report_metrics.asyncio_detailed,
            # Add other versions here when available
        }

        # Convert various input formats to ReportMetricsRequest
        if isinstance(metrics, list):
            # Auto-wrap list of metrics with "metrics" key
            metrics = {"metrics": metrics}

        # Convert dict to ReportMetricsRequest
        if isinstance(metrics, dict):
            metrics = self._convert_dict_to_model(metrics, ReportMetricsRequest)

        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                client=self.client,
                x_org_slug=self.org_slug,
                id=connector_id,
                body=metrics,
            )
            return await self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    async def heartbeat(
        self, connector_id: str, version: Optional[str] = "v1"
    ) -> Response[Any]:
        """
        Sends a heartbeat signal to the Tetra Data Platform.

        Args:
            connector_id: The ID of the connector.
            version: The API version to use. Defaults to "v1".

        Raises:
            ValueError: If the API version is unsupported.

        Returns:
            The response from the API.
        """
        api_version_map = {
            "v1": connector_controller_heartbeat.asyncio_detailed,
            # Add other versions here when available
        }

        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                client=self.client,
                id=connector_id,
                x_org_slug=self.org_slug,
            )
            return await self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    async def update_health(
        self,
        connector_id: str,
        update_connector_health_request: Union[UpdateConnectorHealthRequest, dict],
        version: Optional[str] = "v1",
    ) -> Response[Any]:
        """
        Updates the health status of a connector.

        Args:
            connector_id: The ID of the connector.
            update_connector_health_request: Update health request. Can be either:
                - An UpdateConnectorHealthRequest object
                - A dictionary with health status fields
            version: The API version to use. Defaults to "v1".

        Raises:
            ValueError: If the API version is unsupported.

        Returns:
            The response from the API.
        """
        api_version_map = {
            "v1": connector_controller_update_health.asyncio_detailed,
            # Add other versions here when available
        }

        # Convert dict to UpdateConnectorHealthRequest if needed
        if isinstance(update_connector_health_request, dict):
            update_connector_health_request = self._convert_dict_to_model(
                update_connector_health_request, UpdateConnectorHealthRequest
            )

        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                client=self.client,
                id=connector_id,
                body=update_connector_health_request,
                x_org_slug=self.org_slug,
            )
            return await self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    async def get_certificates(self) -> List[CertificateDto]:
        """
        get certificates stored in TDP org

        Returns:
            List of certificate objects

        Raises:
            TdpApiError: If the API call fails
        """
        self.logger.info("Getting certificates from TDP")

        try:
            # Make a direct request to the certificates endpoint
            # This endpoint is not part of the OpenAPI generated code
            response = await self.client.get_async_httpx_client().get(
                "/v1/certificates",
                params={"includeContent": "true", "includeDisabled": "false"},
                headers={"x-org-slug": self.org_slug},
            )
            response.raise_for_status()

            # Parse the response
            certificates_data = response.json()
            if isinstance(certificates_data, list):
                certificates = [CertificateDto(**cert) for cert in certificates_data]
                self.logger.info(f"Retrieved {len(certificates)} certificates from TDP")
                return certificates
            else:
                self.logger.warning(
                    "Unexpected response format from certificates endpoint"
                )
                return []

        except Exception as e:
            self.logger.error(f"Failed to get certificates: {e}", exc_info=True)
            raise TdpApiError(f"Failed to get certificates: {e}")

    async def create_httpx_instance(
        self,
        base_url: str,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
        verify: bool = True,
    ) -> httpx.AsyncClient:
        """
        Create an httpx async client with TDP certificates for third-party communication.

        This method creates an httpx client with certificates obtained from the TDP
        certificates endpoint. These certificates are used to establish secure
        connections with third-party services.

        The client is also configured with the default certificate bundle to ensure
        it can connect to standard HTTPS endpoints.

        Args:
            base_url: The base URL for the client
            timeout: Optional timeout in seconds
            headers: Optional headers to include in requests
            verify: Flag to control SSL verification. If True (default),
                   uses SSL context with TDP certificates. If False, disables SSL
                   verification entirely.

        Returns:
            An httpx AsyncClient configured with TDP certificates

        Raises:
            TdpApiError: If the client creation fails
        """
        self.logger.info(f"Creating httpx instance for {base_url}")

        try:
            if verify:
                # Use SSL context with TDP certificates
                # Get certificates from TDP
                certificates = await self.get_certificates()

                # Create SSL context with default certificates
                ssl_context = ssl.create_default_context()

                # Load default certificates from certifi
                default_cert_path = certifi.where()
                self.logger.info(
                    f"Loading default certificates from {default_cert_path}"
                )

                # Add TDP certificates
                for cert in certificates:
                    ssl_context.load_verify_locations(cadata=cert.content)

                # Log certificate stats
                cert_stats = ssl_context.cert_store_stats()
                self.logger.info(f"SSL context loaded with certificates: {cert_stats}")

                verify_setting = ssl_context
            else:
                # Disable SSL verification
                verify_setting = False
                self.logger.info("SSL verification disabled")

            # Create httpx client
            client = httpx.AsyncClient(
                base_url=base_url,
                verify=verify_setting,
                timeout=timeout,
                headers=headers or {},
            )

            self.logger.info(f"Created httpx instance for {base_url}")
            return client

        except Exception as e:
            self.logger.error(f"Failed to create httpx instance: {e}", exc_info=True)
            raise TdpApiError(f"Failed to create httpx instance: {e}")

    async def upload_file(
        self,
        request: UploadFileRequest,
        connector_details: Optional[ConnectorDetailsDto] = None,
        strict_mtl_validation: bool = False,
    ) -> UploadFileResponse:
        """
        Asynchronously uploads a file to the datalake.

        Args:
            request: Upload file request.
            connector_details: Optional connector details.
                Used to merge connector metadata, tags, and labels (MTL) for the uploaded file.
                By default, MTL data is merged with the MTL in the connector details, unless
                the `Replace` directive is supplied to the request.
                Refer to the `tags_directive`, `labels_directive`, and `metadata_directive`
                attributes in :class:`UploadFileRequest` for additional information.
            strict_mtl_validation: Whether to throw an error if the request MTL is invalid.
                If false, will just log a warning.

        Returns:
            The upload file response
        """
        uploader = FileUploader(connector_details=connector_details, config=self.config)
        api_call = lambda: uploader.upload_file(
            request, strict_mtl_validation=strict_mtl_validation
        )
        return await self._call_with_error_handling(api_call)
