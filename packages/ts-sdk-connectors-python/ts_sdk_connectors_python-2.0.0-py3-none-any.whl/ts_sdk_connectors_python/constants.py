from typing import Final, Iterator

from ts_sdk_connectors_python.utils import get_public_cls_attrs


class ByteSizes:
    KB = 1024
    MB = 1024**2
    GB = 1024**3


# Path to the Hub proxy environment file
HUB_PROXY_PATH = "/etc/hub/proxy.env"

MAX_EMBEDDED_MESSAGE_SIZE: Final[int] = 256 * ByteSizes.KB
DEFAULT_SQS_QUEUE_WAIT_TIME_SECONDS: Final[int] = 20
DEFAULT_CLOUDWATCH_BUFFER_LIMIT: Final[int] = 5000
DEFAULT_CLOUDWATCH_FLUSH_LIMIT: Final[int] = 100
DEFAULT_CLOUDWATCH_FLUSH_INTERVAL: Final[int] = 30 * 1000  # in milliseconds
MAX_CLOUDWATCH_EVENT_SIZE_BYTES = 256 * ByteSizes.KB
MAX_CLOUDWATCH_BATCH_SIZE_BYTES = 1 * 1024 * ByteSizes.KB
MAX_CLOUDWATCH_BATCH_SIZE_EVENTS = 10 * 1000
# The default timeout for requests made by httpx clients
DEFAULT_HTTPX_TIMEOUT_SECONDS: Final[float] = 10.0
# The min time for SQS clients to respond. Note this is different from the receive_messages long poll values
DEFAULT_SQS_TIMEOUT_SECONDS: Final[float] = 20.0

TS_SDK = "TS_SDK"  # connector SDK settings
TS_SDK_DISABLE_USER_AGENT_HTTP_HEADER = "TS_SDK_DISABLE_USER_AGENT_HTTP_HEADER"


class EnvVars:
    # environment variables
    AWS_REGION = "AWS_REGION"
    ORG_SLUG = "ORG_SLUG"
    HUB_ID = "HUB_ID"
    CONNECTOR_ID = "CONNECTOR_ID"
    DATALAKE_BUCKET = "DATALAKE_BUCKET"
    STREAM_BUCKET = "STREAM_BUCKET"
    TDP_CERTIFICATE_KEY = "TDP_CERTIFICATE_KEY"
    JWT_TOKEN_PARAMETER = "JWT_TOKEN_PARAMETER"
    TDP_ENDPOINT = "TDP_ENDPOINT"
    OUTBOUND_COMMAND_QUEUE = "OUTBOUND_COMMAND_QUEUE"
    KMS_KEY_ID = "KMS_KEY_ID"
    ARTIFACT_TYPE = "ARTIFACT_TYPE"
    CONNECTOR_TOKEN = "CONNECTOR_TOKEN"
    LOCAL_CERTIFICATE_PEM_LOCATION = "LOCAL_CERTIFICATE_PEM_LOCATION"
    CLOUDWATCH_BUFFER_LIMIT = "CLOUDWATCH_BUFFER_LIMIT"
    CLOUDWATCH_FLUSH_LIMIT = "CLOUDWATCH_FLUSH_LIMIT"
    CLOUDWATCH_FLUSH_INTERVAL = "CLOUDWATCH_FLUSH_INTERVAL"
    SKIP_CLOUDWATCH = "SKIP_CLOUDWATCH"
    TDP_TLS_REJECT_UNAUTHORIZED = "TDP_TLS_REJECT_UNAUTHORIZED"

    @classmethod
    def iter(cls) -> Iterator[str]:
        return iter(get_public_cls_attrs(cls))


DEFAULT_LOCAL_CERTIFICATE_FILE: Final[str] = "/etc/tetra/tdp-cert-chain.pem"
