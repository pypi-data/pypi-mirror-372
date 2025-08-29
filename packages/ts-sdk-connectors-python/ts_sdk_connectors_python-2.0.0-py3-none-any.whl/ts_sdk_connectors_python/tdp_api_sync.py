import asyncio
import ssl
import threading
from typing import Any, Callable, Dict, List, Optional, Self, Union

import certifi
import httpx

from ts_sdk_connectors_python.file_uploader import (
    FileUploader,
    UploadFileRequest,
    UploadFileResponse,
)
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


class TdpApiSync(_TdpApiBase):
    """
    This class exposes methods to interact with the Tetra Data Platform REST API.

    All API Calls are synchronous (no async/await).
    """

    def _call_with_error_handling(self, func: Callable):
        """Execute a function with error handling for sync operations"""
        try:
            return func()
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

    def init_client(
        self, proxy_url: Optional[str] = None, disable_verify: bool = False
    ) -> Self:
        """
        Synchronous version of the base class's init_client method
        """
        base_class = super(TdpApiSync, self)
        try:
            asyncio.get_running_loop()
            loop_is_running = True
        except RuntimeError:
            loop_is_running = False

        if loop_is_running:
            # with a running event loop, can't use asyncio.run or loop.run_until_complete
            # so spin off a new thread and run there
            result = None
            exception = None

            def run_in_thread():
                nonlocal result, exception
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        base_class.init_client(proxy_url, disable_verify)
                    )
                    loop.close()
                except Exception as e:
                    exception = e

            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join()

            if exception:
                raise exception
            return result
        else:
            return asyncio.run(base_class.init_client(proxy_url, disable_verify))

    def get_connector_by_id(
        self,
        connector_id: str,
        resolve_secrets: Optional[bool] = None,
        version: Optional[str] = "v1",
    ) -> Response[ConnectorDetailsDto]:
        """
        Synchronously get connector DTO
        GET /v1/data-acquisition/connectors/{id}
        """
        api_version_map = {
            "v1": connector_controller_get_by_id.sync_detailed,
            # Add other versions here if needed
        }

        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                client=self.client,
                x_org_slug=self.org_slug,
                id=connector_id,
                resolve_secrets=resolve_secrets,
            )
            return self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    def get_connector_config(
        self,
        connector_id: str,
        connector_version: Optional[str] = "",
        version: Optional[str] = "v1",
    ) -> Response[Any]:
        """
        Synchronously gets connector config
        GET `/v1/data-acquisition/connectors/${id}/config/${query?.version}`
        """
        api_version_map = {
            "v1": connector_controller_get_config.sync_detailed,
            # Add other versions here if needed
        }

        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                client=self.client,
                id=connector_id,
                version=connector_version,
                x_org_slug=self.org_slug,
            )
            return self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    # TODO: add use_object_notation support
    def get_connector_data(
        self,
        connector_id: str,
        keys: Union[Unset, str] = UNSET,
        version: Optional[str] = "v1",
    ) -> Response[ConnectorDataResponse]:
        """
        Synchronously gets connector data from the key-value store
        GET /v1/connectors/{id}/data

        :param connector_id: The ID of the connector
        :param keys: Optional comma-separated list of keys to filter the results
        :param version: API version to use
        :return: Response containing connector data
        """
        api_version_map = {
            "v1": connector_controller_get_data.sync_detailed,
            # Add other versions here if needed
        }

        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                client=self.client,
                id=connector_id,
                keys=keys,
                x_org_slug=self.org_slug,
            )
            return self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    def save_connector_data(
        self,
        connector_id: str,
        raw_data: Union[SaveConnectorDataRequest, dict, List[dict]],
        version: Optional[str] = "v1",
    ) -> Response[ConnectorDataResponse]:
        """
        Synchronously saves connector data in the key-value store
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
            "v1": connector_controller_save_data.sync_detailed,
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
                client=self.client, id=connector_id, x_org_slug=self.org_slug, body=body
            )
            return self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    def get_connector_files(
        self,
        connector_id: str,
        get_connector_files_query_params={},
        version: Optional[str] = "v1",
    ) -> Response[ConnectorFilesResponse]:
        """
        Synchronously retrieves files uploaded by a connector.

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
            version: The API version to use. Defaults to "v1".

        Raises:
            ValueError: If the API version is unsupported.

        Returns:
            The response from the API.
        """
        api_version_map = {
            "v1": connector_controller_get_files.sync_detailed,
            # Add other versions here when available
        }
        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                client=self.client,
                id=connector_id,
                x_org_slug=self.org_slug,
                **get_connector_files_query_params,
            )
            return self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    def update_connector_files(
        self,
        connector_id: str,
        files_data: Union[SaveConnectorFilesRequest, dict, List[dict]],
        version: Optional[str] = "v1",
    ) -> Response[SaveConnectorFilesResponse]:
        """
        Synchronously updates files associated with a connector.

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
            "v1": connector_controller_update_files.sync_detailed,
            # Add other versions here when available
        }

        # Convert various input formats to SaveConnectorFilesRequest
        if isinstance(files_data, list):
            # Auto-wrap list of file dictionaries with "files" key
            files_data = {"files": files_data}

        # Convert dict to SaveConnectorFilesRequest if needed
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
            return self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    def report_metrics(
        self,
        connector_id: str,
        metrics: Union[ReportMetricsRequest, dict, List[dict]],
        version: Optional[str] = "v1",
    ) -> Response[Any]:
        """
        Synchronously reports metrics to the Tetra Data Platform.

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
            "v1": connector_controller_report_metrics.sync_detailed,
            # Add other versions here when available
        }

        # Convert various input formats to ReportMetricsRequest
        if isinstance(metrics, list):
            # Auto-wrap list of metric dictionaries with "metrics" key
            metrics = {"metrics": metrics}

        # Convert dict to ReportMetricsRequest
        if isinstance(metrics, dict):
            metrics = self._convert_dict_to_model(metrics, ReportMetricsRequest)

        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                id=connector_id,
                client=self.client,
                x_org_slug=self.org_slug,
                body=metrics,
            )
            return self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    def heartbeat(
        self, connector_id: str, version: Optional[str] = "v1"
    ) -> Response[Any]:
        """
        Synchronously sends a heartbeat signal to the Tetra Data Platform.

        Args:
            connector_id: The ID of the connector.
            version: The API version to use. Defaults to "v1".

        Raises:
            ValueError: If the API version is unsupported.

        Returns:
            The response from the API.
        """
        api_version_map = {
            "v1": connector_controller_heartbeat.sync_detailed,
            # Add other versions here when available
        }

        if version in api_version_map:
            api_call = lambda: api_version_map[version](
                client=self.client,
                id=connector_id,
                x_org_slug=self.org_slug,
            )
            return self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    def update_health(
        self,
        connector_id: str,
        update_connector_health_request: Union[UpdateConnectorHealthRequest, dict],
        version: Optional[str] = "v1",
    ) -> Response[Any]:
        """
        Synchronously changes the health status of a connector.

        Args:
            connector_id: The ID of the connector.
            update_connector_health_request: Update health request. Can be either:
                - An UpdateConnectorHealthRequest object
                - A dictionary matching UpdateConnectorHealthRequest structure with fields like
                  "status", "error_code".
            version: The API version to use. Defaults to "v1".

        Raises:
            ValueError: If the API version is unsupported.

        Returns:
            The response from the API.
        """
        api_version_map = {
            "v1": connector_controller_update_health.sync_detailed,
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
            return self._call_with_error_handling(api_call)
        else:
            raise ValueError(f"Unsupported API version: {version}")

    def get_certificates(self) -> List[CertificateDto]:
        """
        Get all enabled CA certificates for the organization.

        This method calls the TDP certificates endpoint to retrieve organization
        certificates that should be trusted for outgoing HTTP requests.

        Returns:
            List of certificate objects

        Raises:
            TdpApiError: If the API call fails
        """
        self.logger.info("Getting certificates from TDP (sync)")

        try:
            # Make a direct request to the certificates endpoint
            # This endpoint is not part of the OpenAPI generated code
            response = self.client.get_httpx_client().get(
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

    def create_httpx_instance(
        self,
        base_url: str,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
        verify: bool = True,
    ) -> httpx.Client:
        """
        Create a synchronous httpx client with TDP certificates for third-party communication.

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
            An httpx Client configured with TDP certificates

        Raises:
            TdpApiError: If the client creation fails
        """
        self.logger.info(f"Creating httpx instance for {base_url} (sync)")

        try:
            if verify:
                # Use SSL context with TDP certificates
                # Get certificates from TDP
                certificates = self.get_certificates()

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

            # Create httpx client (synchronous)
            client = httpx.Client(
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

    def upload_file(
        self,
        request: UploadFileRequest,
        connector_details: Optional[ConnectorDetailsDto] = None,
        strict_mtl_validation: bool = False,
    ) -> UploadFileResponse:
        """
        Uploads a file to the datalake.

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
        api_call = lambda: asyncio.run(
            uploader.upload_file(request, strict_mtl_validation=strict_mtl_validation)
        )
        return self._call_with_error_handling(api_call)
