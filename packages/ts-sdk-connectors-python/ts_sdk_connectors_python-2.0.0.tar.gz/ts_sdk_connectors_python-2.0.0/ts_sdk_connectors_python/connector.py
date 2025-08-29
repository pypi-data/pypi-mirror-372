import asyncio
import inspect
import json
import logging
import textwrap
from http import HTTPStatus
from json import JSONDecodeError
from typing import Any, Callable, Dict, List, Literal, Optional, Union

import pydantic
from pydantic import BaseModel

from ts_sdk_connectors_python.command_listener import CommandListener
from ts_sdk_connectors_python.constants import (
    TS_SDK,
    TS_SDK_DISABLE_USER_AGENT_HTTP_HEADER,
)
from ts_sdk_connectors_python.custom_commands import (
    CommandsByActionDict,
    collect_commands_by_actions,
)
from ts_sdk_connectors_python.file_uploader import UploadFileRequest, UploadFileResponse
from ts_sdk_connectors_python.logger import (
    CloudWatchLoggingManager,
    get_root_connector_sdk_logger,
    set_root_connector_sdk_log_level,
)
from ts_sdk_connectors_python.manifest import ConnectorManifest, get_connector_manifest
from ts_sdk_connectors_python.metrics import (
    CpuMetricsProvider,
    MemoryAvailableProvider,
    MemoryUsedProvider,
    MetricDataPoint,
    MetricsCollector,
    MetricsCollectorOptions,
)
from ts_sdk_connectors_python.models import (
    CommandAction,
    CommandRequest,
    CommandStatus,
    HealthStatus,
    OperatingStatus,
    RegisteredCommandInfo,
)
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.errors import (
    UnexpectedStatus,
)
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.models import (
    ConnectorControllerGetFilesOrderDirection,
    ConnectorControllerGetFilesStatusesItem,
    ConnectorDetailsDto,
    ConnectorDetailsDtoConfig,
    ConnectorFileDto,
    ConnectorFilesResponse,
    ConnectorValueDto,
    MetricTimeValueDto,
    ReportConnectorMetricRequest,
    ReportMetricsRequest,
    SaveConnectorDataRequest,
    SaveConnectorFileRequest,
    SaveConnectorFilesRequest,
    SaveConnectorFilesResponse,
    SaveConnectorValueRequest,
    SaveConnectorValueRequestValue,
)
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.types import (
    Response,
)
from ts_sdk_connectors_python.tdp_api import TdpApi
from ts_sdk_connectors_python.utils import TaskManager, poll_forever


class ConnectorOptions(BaseModel):
    metrics_collection_options: Optional[MetricsCollectorOptions] = None
    metrics_cpu_collection_interval_s: Optional[int] = None
    heartbeat_interval: Optional[int] = 30


class ConnectorError(Exception):
    """Generic connector exceptions"""


class RegisteredCommandDefinedIncorrectly(Exception):
    """Exception raised when a custom command is improperly registered"""


class UnknownCommandError(Exception):
    """Exception raised when an unknown command is requested"""

    def __init__(self, action: str):
        super().__init__(f"Unknown command action: {action}")


class ValidateByConfigVersionBody(BaseModel):
    version: str


class SetLogLevelBody(BaseModel):
    level: Literal[
        "notset",
        "debug",
        "info",
        "warning",
        "error",
        "critical",
        "NOTSET",
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]


class Connector:
    def __init__(
        self,
        tdp_api: TdpApi,
        options: Optional[ConnectorOptions] = None,
    ):
        """
        Initialize a Connector.

        :param tdp_api: The TDPApi instance to use to connect to TDP.
        :param options: Additional connector options.
        """
        self.options = options or ConnectorOptions()
        self.tdp_api = tdp_api
        self.task_manager = TaskManager()
        self._command_listener = None
        self._metrics_collector = None
        self._connector: ConnectorDetailsDto | None = None
        self._custom_commands: CommandsByActionDict | None = None
        self._logger = self.tdp_api.logger.get_child(self.__class__.__name__)
        self._manifest = self._load_connector_manifest()
        self._default_user_agent_info = {}
        self._force_idle_for_failed_on_start = False

    def _load_connector_manifest(self) -> ConnectorManifest | None:
        manifest = get_connector_manifest()
        if manifest:
            self._logger.info(
                "Connector manifest.json loaded",
                extra={"manifest": manifest.model_dump_json()},
            )
        else:
            self._logger.info("Connector manifest.json not loaded")
        return manifest

    @property
    def logger(self):
        return self._logger

    @property
    def connector_id(self) -> str | None:
        return self.tdp_api.config.connector_id

    @property
    def connector_details(self) -> ConnectorDetailsDto:
        if not self.connector_details_are_loaded():
            raise ConnectorError("Connector information is not loaded")
        return self._connector

    def connector_details_are_loaded(self) -> bool:
        return self._connector is not None

    @property
    def connector_config(self) -> ConnectorDetailsDtoConfig:
        if not isinstance(self.connector_details.config, ConnectorDetailsDtoConfig):
            raise ConnectorError("Connector config information is not loaded")
        return self.connector_details.config

    async def upload_file(
        self, request: UploadFileRequest, strict_mtl_validation: bool = False
    ) -> UploadFileResponse:
        """
        Upload file to datalake. This method uploads the file asynchronously.

        See :meth:`Connector.sync_upload_file` for the synchronous version.

        **MTL Directives:**

        MTL (Metadata, Tags, and Labels) directives determine how new MTL data is applied.

        - `Replace`: Overwrites existing metadata, tags, or labels.
        - `Append`: Adds new metadata, tags, or labels while preserving existing ones.

        :param request: Upload file request
        :param strict_mtl_validation: If true, invalid MTL directives will cause an error.
         When disabled, invalid MTL configurations will only generate a warning in logs.
        :return: The upload file response
        """
        if not self.connector_details_are_loaded():
            await self.load_connector_details(False)
        return await self.tdp_api.upload_file(
            request=request,
            connector_details=self.connector_details,
            strict_mtl_validation=strict_mtl_validation,
        )

    def sync_upload_file(
        self, request: UploadFileRequest, strict_mtl_validation: bool = False
    ) -> UploadFileResponse:
        """
        Upload file to datalake. This method uploads the file synchronously.

        See :meth:`Connector.upload_file` for the async version.

        **MTL Directives:**

        MTL (Metadata, Tags, and Labels) directives determine how new MTL data is applied.

        - `Replace`: Overwrites existing metadata, tags, or labels.
        - `Append`: Adds new metadata, tags, or labels while preserving existing ones.

        :param request: Upload file request
        :param strict_mtl_validation: If true, invalid MTL directives will cause an error.
         When disabled, invalid MTL configurations will only generate a warning in logs.
        :return: The upload file response
        """
        if not self.connector_details_are_loaded():
            asyncio.run(self.load_connector_details(False))
        return asyncio.run(
            self.tdp_api.upload_file(
                request=request,
                connector_details=self.connector_details,
                strict_mtl_validation=strict_mtl_validation,
            )
        )

    async def load_connector_details(self, emit_event: bool = True):
        prev_connector_details = None
        if self.connector_details_are_loaded():
            prev_connector_details = self.connector_details
        await self.reload_connector_details()
        if emit_event:
            await self.on_connector_updated(prev_connector_details)

    def log_response_error(
        self,
        response: Response,
        *,
        error_context: Optional[str] = None,
        should_throw: bool = False,
    ):
        """Log an error if the openapi http response indicates an errored status code."""
        err_msg = ""
        if 400 <= response.status_code < 500:
            response.json()
            err_msg = f"Client error {response.status_code}"
        if 500 <= response.status_code < 600:
            err_msg = f"Server error {response.status_code}"
        if err_msg:
            content = response.content
            # just try to get meaningful stuff from the content
            try:
                content = json.loads(content)
            except JSONDecodeError:
                try:
                    content = content.decode("utf-8")
                except UnicodeDecodeError:
                    pass
            if error_context:
                err_msg = err_msg + ": " + error_context
            self.logger.error(err_msg, extra={"error": content})
            if should_throw:
                raise ConnectorError(err_msg)

    async def reload_connector_details(self):
        resp = await self.tdp_api.get_connector_by_id(
            self.connector_id,
            resolve_secrets=True,
            include=["config", "artifact"],
        )
        self.log_response_error(resp, error_context="get_connector_by_id")
        self._connector = resp.parsed
        await self._configure_user_agent()

    async def get_connector(
        self,
        resolve_secrets: Optional[bool] = None,
        include: Optional[List[str]] = None,
    ) -> ConnectorDetailsDto:
        """
        Get connector details from TDP.

        :param resolve_secrets: Whether to resolve secrets in the connector details.
        :param include: List of sections to include in the response (e.g., ["config", "artifact"]).
        :return: The connector details.
        """
        if include is None:
            include = ["config", "artifact"]

        resp = await self.tdp_api.get_connector_by_id(
            self.connector_id,
            resolve_secrets=resolve_secrets,
            include=include,
        )
        self.log_response_error(
            resp, error_context="get_connector_by_id", should_throw=True
        )
        if resp.status_code != HTTPStatus.OK:
            raise ConnectorError(
                f"Failed to get connector. Status code: {resp.status_code}"
            )
        return resp.parsed

    async def get_config(self, version: Optional[str] = None) -> Any:
        """
        Get connector configuration from TDP.

        :param version: The version of the configuration to retrieve.
        :return: The connector configuration.
        """
        resp = await self.tdp_api.get_connector_config(
            self.connector_id,
            connector_version=version,
        )
        self.log_response_error(
            resp, error_context="get_connector_config", should_throw=True
        )
        if resp.status_code != HTTPStatus.OK:
            raise ConnectorError(
                f"Failed to get connector config. Status code: {resp.status_code}"
            )
        return json.loads(resp.content)

    async def get_value(self, key: str) -> ConnectorValueDto | None:
        """
        Get a single value from the connector data store.

        :param key: The key of the value to retrieve.
        :return: The value associated with the key.
        """
        values = await self.get_values([key])
        if not isinstance(values, list):
            raise ConnectorError(
                f"Failed to get connector data. Expected list, got {type(values)}"
            )
        if len(values) == 0:
            self.logger.warning(
                f"Expected 1 value for key {key}, got 0. Key may not exist."
            )
            return None
        elif len(values) > 1:
            raise ConnectorError(f"Expected 1 value for key, got {len(values)}")
        return values[0]

    async def get_values(self, keys: List[str]) -> List[ConnectorValueDto]:
        """
        Get multiple values from the connector data store.

        :param keys: The keys of the values to retrieve.
        :return: A list of values associated with the keys.
        """
        # Use server-side filtering by passing keys as comma-separated string
        keys_filter = ",".join(keys) if keys else None
        resp = await self.tdp_api.get_connector_data(
            self.connector_id, keys=keys_filter
        )
        self.log_response_error(
            resp, error_context="get_connector_data", should_throw=True
        )

        if resp.status_code != HTTPStatus.OK:
            raise ConnectorError(
                f"Failed to get connector data. Status code: {resp.status_code}"
            )
        # None induced by the codegen parser if response is not 200 should be taken
        # care of by the previous lines
        if resp.parsed and resp.parsed.values:
            return resp.parsed.values
        return []

    async def save_value(
        self, key: str, value: dict, secure: bool = False
    ) -> ConnectorValueDto:
        """
        Save a single value to the connector data store.

        :param key: The key to associate with the value.
        :param value: The value to save. This must be structured as a dictionary
        :param secure: Whether to store the value securely.
        :return: The saved value.
        """
        scvrv = SaveConnectorValueRequestValue.from_dict(value)
        request = SaveConnectorValueRequest(key=key, value=scvrv, secure=secure)
        resp = await self.save_values([request])
        if len(resp) == 0:
            # unlike get_value, where get_values can sensibly return an empty
            # list, here there's probably some kind of issue if we didn't get
            # back the value we just added
            raise ConnectorError("Saving connector data didn't return updated value")
        elif len(resp) > 1:
            raise ConnectorError(
                f"Saving connector data returned multiple values, expected 1"
            )
        return resp[0]

    async def save_values(
        self, values: Union[dict, List[dict], List[SaveConnectorValueRequest]]
    ) -> List[ConnectorValueDto]:
        """
        Save multiple values to the connector data store.

        If passed a dict, each key-value pair in the dict will be written as an
        insecure value. If you pass a list of dicts, the dict should have keys
        `key`, `value`, and (optionally) `secure`

        :param values: The values to save.
        :return: A list of saved values.
        """

        standardized_values: List[SaveConnectorValueRequest] = []
        if isinstance(values, dict):
            for k, v in values.items():
                scvrv = SaveConnectorValueRequestValue.from_dict(v)
                standardized_values.append(
                    SaveConnectorValueRequest(key=k, value=scvrv)
                )
        elif not isinstance(values, list):
            raise ValueError(
                "Argument to save_values must be a dict, list of SaveConnectorValueRequest, or list of dicts specifying 'key' and 'value'"
            )
        else:
            for v in values:
                if isinstance(v, dict):
                    try:
                        scvrv = SaveConnectorValueRequestValue.from_dict(v["value"])
                        standardized_values.append(
                            SaveConnectorValueRequest(
                                key=v["key"], value=scvrv, secure=v.get("secure", False)
                            )
                        )
                    except Exception as exc:
                        raise ValueError(
                            f"save_values failed to convert dict to SaveConnectorValueRequest: {exc}"
                        )
                elif isinstance(v, SaveConnectorValueRequest):
                    standardized_values.append(v)
                else:
                    raise ValueError(
                        "Argument to save_values must be a dict, list of SaveConnectorValueRequest, or list of dicts specifying 'key' and 'value'"
                    )

        request = SaveConnectorDataRequest(values=standardized_values)
        resp = await self.tdp_api.save_connector_data(self.connector_id, request)
        self.log_response_error(
            resp, error_context="save_connector_data", should_throw=True
        )

        # 200 is still expected status code here, per OpenAPI and data acq
        # code
        if resp.status_code != HTTPStatus.OK:
            raise ConnectorError(
                f"Failed to save connector data. Status code: {resp.status_code}"
            )
        if resp.parsed and resp.parsed.values:
            return [dto for dto in resp.parsed.values]
        return []

    async def get_files(
        self,
        query_params: Optional[Dict[str, Any]] = None,
        *,
        file_ids: Optional[List[str]] = None,
        exclude_file_ids: Optional[List[str]] = None,
        unique_external_ids: Optional[List[str]] = None,
        exclude_unique_external_ids: Optional[List[str]] = None,
        statuses: Optional[List[str | ConnectorControllerGetFilesStatusesItem]] = None,
        max_errors: Optional[int] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None,
        order_by: Optional[str] = None,
        order_direction: Optional[
            str | ConnectorControllerGetFilesOrderDirection
        ] = None,
        paginate: bool = True,
        page_size: Optional[int] = 100,
        max_results: Optional[int] = None,
        _max_pages: Optional[int] = 1000,
    ) -> ConnectorFilesResponse | None:
        """
        Get files associated with the connector.

        :param query_params: Query parameters for filtering and sorting the files.
            Additional parameters not covered by explicit arguments can be passed here.
            Explicit parameters take precedence over values in this dict.
        :param file_ids: List of file IDs to include.
        :param exclude_file_ids: List of file IDs to exclude.
        :param unique_external_ids: List of unique external IDs to include.
        :param exclude_unique_external_ids: List of unique external IDs to exclude.
        :param statuses: List of processing statuses to include. Valid values: 'ERROR', 'PENDING', 'PROCESSING', 'SKIPPED', 'SUCCESS'.
        :param max_errors: Maximum number of errors allowed.
        :param take: Number of records to take.
        :param skip: Number of records to skip.
        :param order_by: Field to order the results by.
        :param order_direction: Direction to order the results. Valid values: 'ASC', 'DESC'.
        :param paginate: Whether to automatically fetch all pages of results. Default: True.
        :param page_size: Number of files to fetch per API call during auto-pagination. Default: 100. Ignored if take is specified.
        :param max_results: Maximum total files to return across all pages. Prevents accidentally fetching huge datasets. Default: None (no limit).
        :param _max_pages: Maximum number of pages for pagination requests. Default: 1000
        :return: The connector files response.
        """
        # Start with query_params dict, then override with explicit parameters
        processed_params = (query_params or {}).copy()

        # Explicit parameters take precedence over dict values
        explicit_params = {
            "file_ids": file_ids,
            "exclude_file_ids": exclude_file_ids,
            "unique_external_ids": unique_external_ids,
            "exclude_unique_external_ids": exclude_unique_external_ids,
            "statuses": statuses,
            "max_errors": max_errors,
            "take": take,
            "skip": skip,
            "order_by": order_by,
            "order_direction": order_direction,
        }
        explicit_params = {k: v for k, v in explicit_params.items() if v is not None}

        # Merge with provided params, explicit params take precedence
        processed_params = {**processed_params, **explicit_params}

        # Convert statuses from strings to enum objects
        if "statuses" in processed_params and processed_params["statuses"] is not None:
            status_enums = []
            for status in processed_params["statuses"]:
                if isinstance(status, str):
                    status_enums.append(ConnectorControllerGetFilesStatusesItem(status))
                else:
                    status_enums.append(status)
            processed_params["statuses"] = status_enums

        # Convert order_direction from string to enum object
        if "order_direction" in processed_params and isinstance(
            processed_params["order_direction"], str
        ):
            processed_params[
                "order_direction"
            ] = ConnectorControllerGetFilesOrderDirection(
                processed_params["order_direction"]
            )

        if paginate:
            return await self._get_files_with_pagination(
                processed_params=processed_params,
                page_size=page_size,
                max_results=max_results,
                max_pages=_max_pages,
            )
        else:
            # Single API call (current behavior)
            resp = await self.tdp_api.get_connector_files(
                connector_id=self.connector_id,
                get_connector_files_query_params=processed_params,
            )
            self.log_response_error(
                resp, error_context="get_connector_files", should_throw=True
            )
            # according to codegen, the only expected status here is 200, and a
            # non-200 would result in parsing returning None if raise_on_unexpected_status is
            # not set. (We don't want to use that globally at the moment because
            # the patterns throughout the connector with logging would probably
            # not be happy if throwing occurs before log_error_response type
            # things)
            if resp.status_code != HTTPStatus.OK:
                raise ConnectorError(
                    f"get_connector_files failed with status code {resp.status_code}"
                )
            return resp.parsed

    async def _get_files_with_pagination(
        self,
        processed_params: Dict[str, Any],
        page_size: int,
        max_results: Optional[int],
        max_pages: int = 1000,
    ) -> ConnectorFilesResponse | None:
        """
        Helper method to fetch all files using auto-pagination.

        :param processed_params: The processed query parameters
        :param page_size: Number of files to fetch per API call
        :param max_results: Maximum total files to return
        :param max_pages: Maximum total pages
        :return: Combined response with all files
        """
        # Extract and handle skip/take parameters
        current_skip = processed_params.get("skip", 0)
        take = processed_params.get("take")

        # Create a copy of processed_params to avoid modifying the original
        page_params = processed_params.copy()
        if "skip" in page_params:
            del page_params["skip"]
        if "take" in page_params:
            del page_params["take"]

        # Determine how many results to fetch
        num_results = (
            take
            if take is not None
            else (max_results if max_results is not None else float("inf"))
        )
        if max_results is not None and take is not None:
            num_results = min(take, max_results)

        all_files: list[ConnectorFileDto] = []
        page_count = 0

        while True:
            if num_results != float("inf") and len(all_files) >= num_results:
                break

            # Backup safeguard to prevent infinite loops
            page_count += 1
            if page_count > max_pages:
                self.logger.warning(
                    f"Max pages ({max_pages}) reached during pagination"
                )
                break

            # Calculate how many items to take for this page
            remaining = (
                num_results - len(all_files)
                if num_results != float("inf")
                else page_size
            )
            current_page_size = min(page_size, remaining)

            # Set parameters for this page
            current_params = {
                **page_params,
                "take": current_page_size,
                "skip": current_skip,
            }

            # Get the page
            page_response = await self.tdp_api.get_connector_files(
                connector_id=self.connector_id,
                get_connector_files_query_params=current_params,
            )
            self.log_response_error(
                page_response, error_context="get_connector_files", should_throw=True
            )

            if page_response.status_code != HTTPStatus.OK:
                raise ConnectorError(
                    f"get_connector_files failed with status code {page_response.status_code}"
                )
            page = page_response.parsed
            if not page.files or len(page.files) == 0:
                break

            # Add files to our result set
            all_files.extend(page.files)
            current_skip += len(page.files)

            # If we got fewer files than requested, we've reached the end
            if len(page.files) < current_page_size:
                break

        # Return combined results
        # page might be None if there was an error in the API response
        total = page.total if page and hasattr(page, "total") else len(all_files)
        return ConnectorFilesResponse(files=all_files, total=total)

    async def save_file(
        self,
        file: Optional[Union[dict, SaveConnectorFileRequest]] = None,
        *,
        id: Optional[str] = None,
        unique_external_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        status: Optional[str] = None,
        error_count: Optional[float] = None,
        error_message: Optional[str] = None,
        filepath: Optional[str] = None,
    ) -> ConnectorFileDto:
        """
        Save a single file.

        :param file: The file to save as a dict or SaveConnectorFileRequest object.
            Provides base values that can be overridden by explicit parameters.
        :param id: File ID. Overrides value in file parameter if provided.
        :param unique_external_id: Unique external identifier for the file. Overrides value in file parameter if provided.
        :param metadata: File metadata as a dictionary. Overrides value in file parameter if provided.
        :param status: File processing status. Overrides value in file parameter if provided.
        :param error_count: Number of errors encountered. Overrides value in file parameter if provided.
        :param error_message: Error message if file processing failed. Overrides value in file parameter if provided.
        :param filepath: Path to the file. Overrides value in file parameter if provided.
        :return: The saved file.
        :raises ConnectorError: If the file save fails.
        :raises ValueError: If neither file parameter nor explicit parameters are provided.
        """
        # Handle hybrid approach: start with file parameter, override with explicit parameters
        if file is not None:
            # Start with provided file object/dict as base
            if isinstance(file, dict):
                file_params = file.copy()
            elif isinstance(file, SaveConnectorFileRequest):
                # Convert SaveConnectorFileRequest to dict for merging
                from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.types import (
                    UNSET,
                )

                file_params = {}
                if file.id is not UNSET and file.id is not None:
                    file_params["id"] = file.id
                if (
                    file.unique_external_id is not UNSET
                    and file.unique_external_id is not None
                ):
                    file_params["unique_external_id"] = file.unique_external_id
                if file.metadata is not UNSET and file.metadata is not None:
                    # Convert metadata object back to dict
                    file_params["metadata"] = file.metadata.additional_properties
                if file.status is not UNSET and file.status is not None:
                    file_params["status"] = file.status
                if file.error_count is not UNSET and file.error_count is not None:
                    file_params["error_count"] = file.error_count
                if file.error_message is not UNSET and file.error_message is not None:
                    file_params["error_message"] = file.error_message
                if file.filepath is not UNSET and file.filepath is not None:
                    file_params["filepath"] = file.filepath
            else:
                raise ValueError(
                    f"save_file expected a dict or SaveConnectorFileRequest, got {type(file)}"
                )
        else:
            file_params = {}

        # Explicit parameters override file values (same pattern as get_files)
        if id is not None:
            file_params["id"] = id
        if unique_external_id is not None:
            file_params["unique_external_id"] = unique_external_id
        if metadata is not None:
            file_params["metadata"] = metadata
        if status is not None:
            file_params["status"] = status
        if error_count is not None:
            file_params["error_count"] = error_count
        if error_message is not None:
            file_params["error_message"] = error_message
        if filepath is not None:
            file_params["filepath"] = filepath

        if not file_params:
            raise ValueError(
                "save_file requires either a 'file' parameter or explicit parameters (id, unique_external_id, etc.)"
            )

        # Handle metadata conversion if needed
        if "metadata" in file_params and isinstance(file_params["metadata"], dict):
            from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.models.save_connector_file_request_metadata import (
                SaveConnectorFileRequestMetadata,
            )

            metadata_obj = SaveConnectorFileRequestMetadata()
            metadata_obj.additional_properties.update(file_params["metadata"])
            file_params["metadata"] = metadata_obj

        try:
            standardized_file = SaveConnectorFileRequest(**file_params)
        except Exception as exc:
            raise ValueError(
                f"save_file failed to create SaveConnectorFileRequest: {exc}"
            )

        resp = await self.save_files([standardized_file])

        if resp.failures and len(resp.failures) > 0:
            failure = resp.failures[0]
            self.logger.error(
                "File save failed",
                extra={
                    "fileId": file.id,
                    "uniqueExternalId": file.unique_external_id,
                    "failure": failure.message if failure else "Unknown error",
                },
            )
            raise ConnectorError(failure.message if failure else "File save failed")

        if resp.files and len(resp.files) > 0:
            return resp.files[0]
        return None

    async def save_files(
        self,
        files: Union[List[dict], List[SaveConnectorFileRequest]],
        *,
        batch_size: Optional[int] = 50,
        throw_on_any_failure: bool = True,
    ) -> SaveConnectorFilesResponse:
        """
        Save multiple files with automatic batching for large lists.

        :param files: The files to save.
        :param batch_size: Maximum number of files to save per API call.
            If None, all files are saved in a single batch. Default: 50.
        :return: The save files response with combined results from all batches.
        """
        # Validate input
        if not isinstance(files, list):
            raise ValueError(
                f"save_files expected a list of either dicts or SaveConnectorFileRequest, got {type(files)}"
            )

        # Convert all files to standardized format
        standardized_files = []
        for single_file in files:
            if isinstance(single_file, dict):
                try:
                    standardized_files.append(SaveConnectorFileRequest(**single_file))
                except Exception as exc:
                    raise ValueError(
                        f"save_files failed to convert dict to SaveConnectorFileRequest: {exc}"
                    )
            elif isinstance(single_file, SaveConnectorFileRequest):
                standardized_files.append(single_file)
            else:
                raise ValueError(
                    f"save_files expected a list of either dicts or SaveConnectorFileRequest, got {type(single_file)}"
                )

        # Determine if batching is needed
        if batch_size is None or len(standardized_files) <= batch_size:
            # Single batch - use existing logic
            request = SaveConnectorFilesRequest(files=standardized_files)
            resp = await self.tdp_api.update_connector_files(self.connector_id, request)
            self.log_response_error(
                resp, error_context="update_connector_files", should_throw=True
            )
            # the resp.parsed is None shouldn't be possible if status_code is
            # 200, but it helps with the type inference
            if resp.status_code != HTTPStatus.OK or resp.parsed is None:
                raise ConnectorError(
                    f"update_connector_files failed with status code {resp.status_code}"
                )
            resp = resp.parsed
        else:
            # Multiple batches needed
            resp = await self._save_files_with_batching(standardized_files, batch_size)
        if throw_on_any_failure and resp.failures and len(resp.failures) > 0:
            err_msg = (
                f"save_files failed on {len(resp.failures)} files; details in logs"
            )
            self.logger.error(err_msg, extra={"failures": resp.failures})
            raise ConnectorError(err_msg)
        return resp

    async def _save_files_with_batching(
        self, standardized_files: List[SaveConnectorFileRequest], batch_size: int
    ) -> SaveConnectorFilesResponse:
        """
        Helper method to save files in batches and combine results.

        :param standardized_files: List of standardized file requests
        :param batch_size: Number of files per batch
        :return: Combined response from all batches
        """
        all_saved_files = []
        all_failures = []

        # Process files in batches
        for i in range(0, len(standardized_files), batch_size):
            batch = standardized_files[i : i + batch_size]

            # Create request for this batch
            batch_request = SaveConnectorFilesRequest(files=batch)

            # Make API call for this batch
            resp = await self.tdp_api.update_connector_files(
                self.connector_id, batch_request
            )
            self.log_response_error(resp, error_context="update_connector_files")

            # Handle batch response
            if resp.parsed:
                if resp.parsed.files:
                    all_saved_files.extend(resp.parsed.files)
                if resp.parsed.failures:
                    all_failures.extend(resp.parsed.failures)
            else:
                # If batch failed completely, log and continue with remaining batches
                self.logger.error(
                    f"Batch {i//batch_size + 1} failed completely",
                    extra={"batch_start": i, "batch_size": len(batch)},
                )

        # Return combined response
        return SaveConnectorFilesResponse(files=all_saved_files, failures=all_failures)

    async def _heartbeat(self):
        """
        Send a heartbeat to the TDP API.

        Successful heartbeats result in the connector being marked ONLINE in TDP
        """
        try:
            resp = await self.tdp_api.heartbeat(self.connector_id)
            self.log_response_error(
                resp, error_context="heartbeat"
            )  # Logs 4xx and 5xx errors
        except Exception as exc:
            # due to the frequent, periodic nature of the heartbeat,
            # transient failures with the heartbeat are common
            # as are deployment/networking related auth, SSL, networking, or timeout errors
            # so we just log them and move on
            self.logger.error("Error sending heartbeat", exc_info=True)

    def init_command_listener(self) -> CommandListener:
        """
        Initialize the command listener

        :return: The command listener object
        """
        command_listener = CommandListener(api_inst=self.tdp_api)
        command_listener.events_emitter.add_listener("command", self.handle_command)
        return command_listener

    def init_metrics_collector(
        self, options: Optional[MetricsCollectorOptions] = None
    ) -> MetricsCollector:
        """
        Initialize the metrics collector

        :return: The metrics collector object
        """

        async def exporter(metric_list: list[MetricDataPoint]):
            """Convert metric data points into the data transfer objects expected by the tdp api"""
            if metric_list:
                metrics_dto_list: list[ReportConnectorMetricRequest] = []

                for metric in metric_list:
                    metrics_dto_list.append(
                        ReportConnectorMetricRequest(
                            name=metric.name,
                            unit=metric.unit,
                            values=[
                                MetricTimeValueDto(
                                    time=metric.point.time, value=metric.point.value
                                )
                            ],
                            dimensions=[],
                        )
                    )
                resp = await self.tdp_api.report_metrics(
                    self.connector_id,
                    ReportMetricsRequest(metrics=metrics_dto_list),
                )
                self.log_response_error(resp, error_context="report_metrics")
                if resp.status_code >= 400 and resp.status_code < 500:
                    raise UnexpectedStatus(resp.status_code, resp.content)
                elif resp.status_code >= 500:
                    raise UnexpectedStatus(resp.status_code, resp.content)

        metrics_collector = MetricsCollector(exporter=exporter, options=options)
        metrics_collector.register_provider(
            CpuMetricsProvider(
                cpu_interval=self.options.metrics_cpu_collection_interval_s
            ),
        )  # collect cpu metrics on 3 second interval
        metrics_collector.register_provider(
            MemoryUsedProvider(),
        )
        metrics_collector.register_provider(
            MemoryAvailableProvider(),
        )
        return metrics_collector

    def start_command_listener(self):
        self.logger.info("Starting command listener")
        self._command_listener.start()

    def stop_command_listener(self):
        self.logger.info("Stopping command listener")
        self._command_listener.stop()

    def start_metrics_collection(self):
        self.logger.info("Starting metrics collection")
        self._metrics_collector.start()

    def stop_metrics_collection(self):
        self.logger.info("Stopping metrics collection")
        self._metrics_collector.stop()

    def start_heartbeat(self):
        self.logger.info("Starting heartbeat")
        task = poll_forever(
            target=self._heartbeat,
            interval=self.options.heartbeat_interval,
            poll_name="heartbeat",
        )
        self.task_manager.add_task(task)

    def stop_heartbeat(self):
        self.logger.info("Stopping heartbeat")
        self.task_manager.cancel("heartbeat")

    async def _has_user_agent_set_to_disabled(self):
        response = await self.tdp_api.get_connector_data(self.connector_id)
        connector_data = response.parsed
        if connector_data is not None:
            for value in connector_data.values:
                if value.key == TS_SDK:
                    data = value.value.additional_properties
                    return data.get(TS_SDK_DISABLE_USER_AGENT_HTTP_HEADER) == "true"
        return False

    def _store_default_user_agent_info_if_does_not_exist(self):
        """
        Saves the default user agent info only if it does not yet exist.

        This is utilized in cases where users would like to revert clients back to
        default user-agent behavior.
        """
        if not self._default_user_agent_info:
            sync_client = self.tdp_api.client.get_httpx_client()
            async_client = self.tdp_api.client.get_async_httpx_client()
            self._default_user_agent_info = {}
            for key, _headers in {
                "client": self.tdp_api.client._headers,
                "sync_client": sync_client.headers,
                "async_client": async_client.headers,
            }.items():
                self._default_user_agent_info[key] = None
                for k in _headers:
                    if k.lower() == "user-agent":
                        self._default_user_agent_info[key] = _headers[k]

    def _revert_user_agent_info(self):
        """
        Revert the user-agent headers to their default values.
        """
        httpx_client = self.tdp_api.client.get_httpx_client()
        async_client = self.tdp_api.client.get_async_httpx_client()

        client_user_agent = self._default_user_agent_info.get("client", None)
        sync_client_user_agent = self._default_user_agent_info.get("sync_client", None)
        async_client_user_agent = self._default_user_agent_info.get(
            "async_client", None
        )

        if client_user_agent:
            self.tdp_api.client._headers["user-agent"] = client_user_agent
        else:
            self.tdp_api.client._headers.pop("user-agent", None)

        if sync_client_user_agent:
            httpx_client.headers["user-agent"] = sync_client_user_agent
        else:
            httpx_client.headers.pop("user-agent", None)

        if async_client_user_agent:
            async_client.headers["user-agent"] = async_client_user_agent
        else:
            async_client.headers.pop("user-agent", None)

    async def _configure_user_agent(self):
        """
        Configures the user-agent header for the tdp_api clients.
        If the manifest.json is present, this will add the 'user-agent'
        header with the value of '<slug> <version>' parsed from the manifest.json.

        If the manifest.json file is not present, a default user-agent of
        'PluggableConnector <Connector Class Name>' will be used.

        :return: None
        """
        self._store_default_user_agent_info_if_does_not_exist()
        disabled_user_agent = await self._has_user_agent_set_to_disabled()
        user_agent = f"PluggableConnector {self.__class__.__name__}"
        if not disabled_user_agent:
            if self._manifest:
                slug = self._manifest.slug
                version = self._manifest.version
                if not version.startswith("v"):
                    version = "v" + version
                user_agent = f"{slug} {version}"
            self.logger.info(f'Configuring user-agent headers to "{user_agent}"')
            self.tdp_api.update_headers({"user-agent": user_agent})
        else:
            self.logger.info(f"Reverting user-agent header")
            self._revert_user_agent_info()

    async def _init_client(self):
        if not self.tdp_api.client_is_initialized():
            self.logger.info("Initializing TDP API client...")
            # Note that Connector is expecting a TdpApi, not a TdpApiSync, so
            # it is probably safe to await this. But it should also be safe to
            # check
            possible_awaitable = self.tdp_api.init_client()
            if inspect.isawaitable(possible_awaitable):
                await possible_awaitable

    async def start(self):
        """
        Connector.start() is one of the first steps in the lifecycle of a connector.

        It will:
        - Initialize TDP API dependencies
        - Load connector details from TDP
        - Start heartbeats, metrics collection, and listening for Commands
        - Call developer-defined hooks for on_initializing, on_start, and on_initialized
        """
        try:
            self.logger.info("Starting connector initialization...")
            await self.on_initializing()

            self.logger.info("Finished on_initializing")
            if not self.tdp_api.client_is_initialized():
                self.logger.info("Initializing TDP API client...")
                await self._init_client()
            self.logger.info("Initializing command listener and metrics collector...")
            self._command_listener = self.init_command_listener()
            self._metrics_collector = self.init_metrics_collector(
                options=self.options.metrics_collection_options
            )
            self.logger.info("Loading connector details...")
            await self.load_connector_details(emit_event=False)

            self.logger.info("Starting heartbeat, metrics, and command listeners...")
            self.start_heartbeat()
            self.start_metrics_collection()
            self.start_command_listener()

            if self.connector_details.operating_status == OperatingStatus.RUNNING:
                self.logger.info("Running on_start...")
                try:
                    await self.on_start()
                    self.logger.info("Finished on_start")
                except Exception as exc:
                    self.logger.error(
                        "Unable to run on_start on connector startup", exc_info=exc
                    )
                    self._force_idle_for_failed_on_start = True
                    await self.tdp_api.update_health(
                        connector_id=self.connector_id,
                        update_connector_health_request={
                            "status": HealthStatus.CRITICAL,
                            "errorCode": "StartAsRunningFailure",
                        },
                    )

            await self.on_initialized()
            self.logger.info(
                "Connector fully started",
                extra={
                    "namespace": self.connector_details.artifact.namespace,
                    "slug": self.connector_details.artifact.slug,
                    "version": self.connector_details.artifact.version,
                    "operating_status": self.connector_details.operating_status,
                },
            )
        except Exception as exc:
            self.logger.error("Unhandled error during connector startup", exc_info=exc)
            raise exc

    async def shutdown(self):
        self.logger.info("Connector shutting down")
        await self.on_shutdown()
        self.stop_metrics_collection()
        self.stop_heartbeat()
        self.logger.info("Connector shutdown complete")
        await CloudWatchLoggingManager.stop_cloudwatch(
            connector_id=self.tdp_api.config.connector_id,
            org_slug=self.tdp_api.config.org_slug,
        )

    async def handle_command(self, command: CommandRequest):
        try:
            resp = await self.try_handle_command(command)
            await self._command_listener.send_command_response(
                command.create_response({"status": CommandStatus.SUCCESS, "body": resp})
            )
            self.logger.debug(
                "Handled command",
                extra={"id": command.commandId, "action": command.action},
            )
        except UnknownCommandError as exception:
            self.logger.error(
                "Unknown command",
                exc_info=exception,
                extra={"id": command.commandId, "action": command.action},
            )
            await self._command_listener.send_command_response(
                command.create_response(
                    {
                        "status": CommandStatus.REJECTED,
                        "body": {"message": str(exception)},
                    }
                )
            )
        except Exception as exception:
            self.logger.error(
                "Command execution error",
                exc_info=exception,
                extra={"id": command.commandId, "action": command.action},
            )
            if (
                command.action == CommandAction.STOP
                and self._force_idle_for_failed_on_start
            ):
                await self._command_listener.send_command_response(
                    command.create_response(
                        {
                            "status": CommandStatus.SUCCESS,
                            "body": {
                                "message": "Connector forced to IDLE because on_start failed when trying to enable the connector as RUNNING"
                            },
                        }
                    )
                )
                self._force_idle_for_failed_on_start = False
            else:
                await self._command_listener.send_command_response(
                    command.create_response(
                        {
                            "status": CommandStatus.FAILURE,
                            "body": {"message": str(exception)},
                        }
                    )
                )

    async def try_handle_command(self, command: CommandRequest):
        """
        Attempt to handle a command request.

        :param command: The command request
        :return: None
        :raises UnknownCommandError: If no handler exists for the `command.action`
        """
        if command.action == CommandAction.START:
            return await self.on_start()
        elif command.action == CommandAction.SHUTDOWN:
            return await self.shutdown()
        elif command.action == CommandAction.STOP:
            return await self.on_stop()
        elif command.action == CommandAction.UPDATE_CONFIG:
            return await self.update_config()
        elif command.action == CommandAction.VALIDATE_CONFIG:
            return await self.validate_config_by_version(command.body)
        elif command.action == CommandAction.LIST_CUSTOM_COMMANDS:
            return self.handle_get_available_custom_commands()
        elif command.action == CommandAction.SET_LOG_LEVEL:
            return self.handle_set_log_level(command.body)
        elif self.has_custom_command(command.action):
            return await self.handle_custom_command(command)
        else:
            raise UnknownCommandError(command.action)

    def handle_set_log_level(self, body: Any):
        if isinstance(body, (str, bytes, bytearray)):
            data = SetLogLevelBody.model_validate_json(body)
        else:
            data = SetLogLevelBody.model_validate(body)

        curr_level = logging.getLevelName(get_root_connector_sdk_logger().level)
        new_level = data.level
        try:
            set_root_connector_sdk_log_level(data.level)
        except Exception as exc:
            self.logger.error(
                msg="Could not set level",
                exc_info=exc,
                extra={"current_level": curr_level, "desired_level": new_level},
            )
        return {"previous_level": curr_level, "desired_level": new_level}

    def handle_get_available_custom_commands(self) -> dict[str, list[dict]]:
        """
        Return the list of information on available custom commands registered to this Connector.

        :return: a dict containing the list of custom command information. See :class:`RegisteredCommandInfo` for expected format.
        """
        command_info = []
        cmd_dict = self._get_custom_commands()

        def format_docstr(docstr):
            if docstr is None:
                return ""
            return textwrap.dedent(docstr).strip()

        for action, command in cmd_dict.items():
            method_name = command.callable.__name__
            signature_str = str(inspect.signature(command.callable))
            command_info.append(
                RegisteredCommandInfo.model_validate(
                    {
                        "action": command.action,
                        "method_name": command.callable.__name__,
                        "documentation": format_docstr(command.callable.__doc__),
                        "signature": f"{method_name}{signature_str}",
                    }
                )
            )
        return {"custom_commands": [info.model_dump() for info in command_info]}

    async def handle_command_fallback(self, command: CommandRequest) -> Any:
        """
        Fallback for when command action has not been handled. By default, this will return a
        message specifying the command request has been successfully handled, but no action was taken.

        :param command: The command request
        :return: The log message
        """
        msg = f"Command action '{command.action}' received, but the handler for it is not implemented. No action was taken."
        self.logger.info(msg)
        raise ConnectorError(msg)

    def _get_custom_commands(self) -> CommandsByActionDict:
        if self._custom_commands is None:
            self._custom_commands = collect_commands_by_actions(self)
        return self._custom_commands

    def has_custom_command(self, action: str) -> bool:
        """
        Return True if there is a custom command registered for this provided action.

        :param action: The provided action name
        :return: True if there is a custom command registered for this provided action
        """
        return action in self._get_custom_commands()

    def _validate_custom_command_signature_or_raise(self, action: str, fn: Callable):
        signature = inspect.signature(fn)
        if not len(signature.parameters) == 1:
            raise RegisteredCommandDefinedIncorrectly(
                f"Could not handle action `{action}`. During connector creation, a handler for this action was "
                f"improperly registered. Methods registered as actions expect one argument, "
                f"but found signature `{fn.__name__}{signature}`"
            )

    async def handle_custom_command(self, command: CommandRequest):
        cmd_dict = self._get_custom_commands()
        cmd = cmd_dict[command.action]

        self._validate_custom_command_signature_or_raise(cmd.action, cmd.callable)
        try:
            result = cmd.callable(command.body)
            if inspect.isawaitable(result):
                result = await result
            return result
        except Exception as exc:
            raise ConnectorError(
                f"Failed to execute custom command for action '{cmd.action}' "
                f"(method_name: '{cmd.callable.__name__}') - Reason: {exc}"
            ) from exc

    async def validate_config_by_version(self, body: Any):
        """
        Validates a connector configuration using the developer-defined `validate_config` method.

        This occurs when a user updates the connector configuration on the platform.

        :param body:
        :return:
        """
        try:
            if isinstance(body, (str, bytes, bytearray)):
                version = ValidateByConfigVersionBody.model_validate_json(body).version
            else:
                version = ValidateByConfigVersionBody.model_validate(body).version
        except pydantic.ValidationError as exc:
            pretty_body = (
                json.dumps(body, ensure_ascii=False)
                if isinstance(body, dict)
                else str(body)
            )
            raise ValueError(
                f'Expected a valid json of the form {{"version": "my-version"}}. Got {pretty_body}'
            )

        self.logger.debug("Validating config by version %s", version)
        config = None
        try:
            resp = await self.tdp_api.get_connector_config(
                self.tdp_api.config.connector_id, connector_version=version
            )
            self.log_response_error(resp, error_context="get_connector_config")
            if resp.status_code == HTTPStatus.OK:
                # according to data-acq service this type
                # should always be a json
                config = json.loads(resp.content)
        except Exception as exc:
            return {
                "valid": False,
                "error": f"Could not get config to validate. Reason - {str(exc)}",
            }

        if config is not None:
            try:
                return await self.validate_config(config)
            except Exception as exc:
                return {
                    "valid": False,
                    "error": f"Could not validate since `validate_config` raised error: {exc}",
                }
        return {"valid": False, "error": "Could not retrieve version to validate"}

    async def update_config(self):
        """
        Loads a new configuration from the data-acquisition service. This occurs after a
        new configuration has been validated and saved to the data-acquisition service.

        This occurs when a user updates the connector configuration on the platform with a
        valid configuration.
        """
        await self.load_connector_details()

    async def on_start(self):
        """
        A developer-defined hook that runs with a 'TetraScience.Connector.Start' command.

        This method is called when the connector state is set to `RUNNING`. It can be used to perform
        any initialization tasks required before the connector begins processing.

        Note that the default implementation of `on_start` will call the `on_connector_updated` method
        when the connector details are loaded.
        """
        self.logger.debug("Connector on_start")
        await self.load_connector_details()

    async def on_stop(self):
        """
        A developer-defined hook that runs with a 'TetraScience.Connector.Stop' command.

        This method is called when the connector state is set to `IDLE`. It can be used to perform
        any cleanup tasks required before the connector stops processing.

        Note that the default implementation of `on_stop` will call the `on_connector_updated` method
        when the connector details are loaded.
        """
        self.logger.debug("Connector on_stop")
        await self.load_connector_details()

    async def on_shutdown(self):
        """
        A developer-defined hook that runs with a 'TetraScience.Connector.Shutdown' command.

        This method is called when the connector is shutting down. It can be used to perform
        any final cleanup tasks required before the connector is completely shut down.
        """

    async def on_connector_updated(self, prev: ConnectorDetailsDto | None):
        """
        A developer-defined hook that runs when the connector's details are updated.

        This method is called when the connector's details are updated. It can be used to
        handle any changes that need to be made when the connector's configuration changes.

        Note that the default implementations of `on_start` and `on_stop` will call this method
        once it loads the connector details.
        """
        self.logger.debug("Connector updated")

    async def on_initializing(self):
        """
        A developer-defined hook that runs when the connector is initializing.

        This method is called during the initial startup phase of the connector. It can be used
        to perform any tasks required to prepare the connector for operation.

        Note: This method only gets called at startup (with the `myconnector.start()`).
        This method does not get called when the connector is updated.
        """

    async def on_initialized(self):
        """
        A developer-defined hook that runs when the connector has finished initializing.

        This method is called after the initial startup phase of the connector. It can be
        used to perform any tasks required after the connector is fully initialized.

        Note: This method only gets called at startup (with the `myconnector.start()`).
        This method does not get called when the connector is updated.
        """

    async def validate_config(self, config: Any) -> dict:
        """
        A developer-defined hook that validates the connector's configuration.

        This method is called to validate the connector's configuration. It should return a dictionary
        with a "valid" key indicating whether the configuration is valid, and optionally an "error" key
        with an error message if the configuration is not valid.

        Example return value:
        .. code-block:: python

            {
                "valid": True
            }

        or

        .. code-block:: python
            {
                "valid": False,
                "error": "Configuration is invalid because..."
            }
        """
        self.logger.debug(
            "Default connector validateConfig implementation always returns true"
        )
        return {
            "valid": True,
        }
