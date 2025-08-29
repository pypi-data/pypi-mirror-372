"""
ts-lib-shared.py

These values are copied from ts-lib-shared-schema and placed here in their own module to easily propagate changes made in
ts-lib-shared-schema to python connectors.

LAST UPDATED FROM: "ts-lib-shared-schema v8.4.1"
"""

from enum import StrEnum
from typing import Final


class S3MetadataFields(StrEnum):
    """Tetrascience's s3 metadata keys for datalake upload"""

    VERSION = "ts_version"

    # Platform metadata fields
    INTEGRATION_ID = "ts_integration_id"
    INTEGRATION_TYPE = "ts_integration_type"
    INTEGRATION_NAME = "ts_integration_name"

    FILE_ID = "ts_file_id"
    FILE_TYPE = "ts_processed_file_type"  # Deprecated
    FILE_PATH = "ts_file_path"
    FILE_NAME = "ts_file_name"
    FILE_CHECKSUM = "ts_file_checksum"
    FILE_SIZE = "ts_file_size"

    TRACE_ID = "ts_trace_id"
    ORIGINAL_FILE_ID = "ts_original_file_id"

    SOURCE_ID = "ts_integration_source"
    SOURCE_TYPE = "ts_source_type"
    SOURCE_NAME = "ts_source_name"
    SOURCE_TIME_ZONE = "ts_source_time_zone"
    DELETED_IN_SOURCE_AT = "ts_deleted_in_source_at"

    RAW_FILE_ID = "ts_source_file_id"
    RAW_FILE_VERSION = "ts_raw_file_version"
    CONTENT_CREATED_FROM_FILE_ID = "ts_content_created_from_file_id"

    DO_NOT_INHERIT_LABELS = "ts_do_not_inherit_labels"

    IDS = "ts_ids"
    IDS_TYPE = "ts_ids_type"
    IDS_VERSION = "ts_ids_type_version"

    AGENT = "ts_agent"
    AGENT_ID = "ts_agent_id"
    AGENT_NAME = "ts_agent_name"

    COMMAND_ID = "ts_command_id"
    CONFIG_CHANGED_BY = "ts_config_changed_by"
    CONFIG_CHANGED_AT = "ts_config_changed_at"

    RAW_MD5_CHECKSUM = "ts_raw_md5_checksum"
    RAW_SHA1_CHECKSUM = "ts_raw_sha1_checksum"
    RAW_SHA256_CHECKSUM = "ts_raw_sha256_checksum"
    RAW_CRC32_CHECKSUM = "ts_raw_crc32_checksum"
    RAW_CRC32C_CHECKSUM = "ts_raw_crc32c_checksum"

    DESTINATION_ID = "ts_destination_id"
    OS_LAST_MODIFIED_TIME = "ts_os_lastmodifiedtime"
    OS_CREATED_TIME = "ts_os_createdtime"
    OS_SIZE_ON_DISK = "ts_os_sizeondisk"
    OS_LAST_MODIFIED_USER = "ts_os_lastmodifieduser"
    OS_CREATED_USER = "ts_os_createduser"
    OS_FILE_PATH = "ts_os_file_path"
    OS_FOLDER_PATH = "ts_os_folder_path"

    API_USER_ID = "ts_user_id"
    API_VIA_WEB = "ts_api_via_web"

    SKIP_PROCESSING = "ts_skip_processing"
    DELETE_MARKER = "ts_delete_marker"

    FILE_LAST_MODIFIED = "ts_file_last_modified"  # Deprecated

    CUSTOM_METADATA = "ts_integration_metadata"
    CUSTOM_TAGS = "ts_integration_tags"

    EGNYTE_URL = "ts_egnyte_url"
    EGNYTE_GROUP_ID = "ts_egnyte_group_id"
    EGNYTE_VERSION_ID = "ts_egnyte_version_id"
    EGNYTE_VERSION_NUM = "ts_egnyte_version_num"

    BOX_FILE_ID = "ts_box_file_id"

    EMAIL_HOST = "ts_email_host"
    EMAIL_HOST_PORT = "ts_email_host_port"
    EMAIL_USERNAME = "ts_email_username"
    EMAIL_FROM = "ts_email_from"
    EMAIL_TO = "ts_email_to"

    HRB_CELLARIO_EVENT_ID = "ts_hrb_cellario_event_id"
    HRB_CELLARIO_EVENT_DATE = "ts_hrb_cellario_event_date"
    HRB_CELLARIO_EVENT_CONTEXT = "ts_hrb_cellario_event_context"
    HRB_CELLARIO_EVENT_TYPE = "ts_hrb_cellario_event_type"
    HRB_CELLARIO_ORDER_ID = "ts_hrb_cellario_order_id"
    HRB_CELLARIO_SYSTEM_NAME = "ts_hrb_cellario_system_name"
    HRB_CELLARIO_URL = "ts_hrb_cellario_url"

    IDBS_EWB_URL = "ts_idbs_ewb_url"
    IDBS_ENTITY_ID = "ts_idbs_entity_id"
    IDBS_ENTITY_NAME = "ts_idbs_entity_name"
    IDBS_ENTITY_TEMPLATE = "ts_idbs_entity_template"
    IDBS_ENTITY_VERSION = "ts_idbs_entity_version"
    IDBS_ENTITY_AUTHOR = "ts_idbs_entity_author"
    IDBS_ENTITY_TIMESTAMP = "ts_idbs_entity_timestamp"

    PIPELINE_ID = "ts_pipeline_id"
    PIPELINE_WORKFLOW_ID = "ts_workflow_id"
    PIPELINE_MASTER_SCRIPT = "ts_master_script"
    PIPELINE_TASK_SCRIPT = "ts_task_script"
    PIPELINE_TASK_SLUG = "ts_task_slug"
    PIPELINE_TASK_EXECUTION_ID = "ts_task_execution_id"
    PIPELINE_HISTORY = "ts_pipeline_history"

    SDC_URL = "ts_sdc_url"
    SDC_INTERFACE_ID = "ts_sdc_interface_id"
    SDC_INTERFACE_RESULT_ID = "ts_sdc_interface_result_id"
    SDC_MEASUREMENT_ID = "ts_sdc_measurement_id"
    SDC_MEASUREMENT_UPDATE_COUNT = "ts_sdc_measurement_update_count"
    SDC_BATCH_NO = "ts_sdc_batch_no"
    SDC_DEVICE_MEASUREMENT_NO = "ts_sdc_device_measurement_no"
    SDC_MEASUREMENT_ON_DEVICE_DATE = "ts_sdc_measurement_on_device_date"

    SOLACE_URL = "ts_solace_url"
    SOLACE_QUEUE_OR_TOPIC_NAME = "ts_solace_queue_or_topic_name"
    SOLACE_CONSUMER_TYPE = "ts_solace_consumer_type"
    SOLACE_CORRELATION_ID = "ts_solace_correlation_id"
    SOLACE_MESSAGE_ID = "ts_solace_message_id"
    SOLACE_VPN_NAME = "ts_solace_vpn_name"

    ANYLINK_GATEWAY_SERIAL_NUMBER = "ts_anylink_gateway_serial_number"
    ANYLINK_DRIVER = "ts_anylink_driver"
    ANYLINK_DRIVER_VERSION = "ts_anylink_driver_version"
    ANYLINK_DEVICE_ID = "ts_anylink_device_id"
    ANYLINK_DEVICE_NAME = "ts_anylink_device_name"
    ANYLINK_DATAITEM = "ts_anylink_dataitem"

    CONNECTOR_NAMESPACE = "ts_connector_namespace"
    CONNECTOR_SLUG = "ts_connector_slug"
    CONNECTOR_VERSION = "ts_connector_version"


class FileCategories(StrEnum):
    RAW = "RAW"
    IDS = "IDS"
    PROCESSED = "PROCESSED"
    TMP = "TMP"


class IntegrationTypes(StrEnum):
    """
    File link integrations
    """

    API = "api"
    HUB = "hub"


class HostType(StrEnum):
    CLOUD = "cloud"
    HUB = "hub"


class SourceTypes(StrEnum):
    UNKNOWN = "unknown"


API_UPLOAD_V1_INTEGRATION_ID: Final[str] = "6f166302-df8a-4044-ab4b-7ddd3eefb50b"
