import os
from typing import Literal, Optional, TypeAlias

from pydantic import BaseModel, Field

from ts_sdk_connectors_python.constants import DEFAULT_LOCAL_CERTIFICATE_FILE, EnvVars

ArtifactType: TypeAlias = Literal["connector"] | Literal["data-app"]


def get_artifact_type() -> ArtifactType:
    artifact_type = os.environ.get(EnvVars.ARTIFACT_TYPE, None)
    if artifact_type == "data-app":
        return "data-app"
    return "connector"


class TdpApiConfig(BaseModel):
    """TdpApi config variables. Pulls from the environment variables, if available."""

    auth_token_provider: Optional[str] = None
    aws_region: Optional[str] = Field(
        default_factory=lambda: os.environ.get(EnvVars.AWS_REGION)
    )
    org_slug: Optional[str] = Field(
        default_factory=lambda: os.environ.get(EnvVars.ORG_SLUG)
    )
    hub_id: Optional[str] = Field(
        default_factory=lambda: os.environ.get(EnvVars.HUB_ID)
    )
    connector_id: Optional[str] = Field(
        default_factory=lambda: os.environ.get(EnvVars.CONNECTOR_ID)
    )
    datalake_bucket: Optional[str] = Field(
        default_factory=lambda: os.environ.get(EnvVars.DATALAKE_BUCKET)
    )
    stream_bucket: Optional[str] = Field(
        default_factory=lambda: os.environ.get(EnvVars.STREAM_BUCKET)
    )
    tdp_certificate_key: Optional[str] = Field(
        default_factory=lambda: os.environ.get(EnvVars.TDP_CERTIFICATE_KEY)
    )
    jwt_token_parameter: Optional[str] = Field(
        default_factory=lambda: os.environ.get(EnvVars.JWT_TOKEN_PARAMETER)
    )
    tdp_endpoint: Optional[str] = Field(
        default_factory=lambda: os.environ.get(EnvVars.TDP_ENDPOINT)
    )
    outbound_command_queue: Optional[str] = Field(
        default_factory=lambda: os.environ.get(EnvVars.OUTBOUND_COMMAND_QUEUE)
    )
    kms_key_id: Optional[str] = Field(
        default_factory=lambda: os.environ.get(EnvVars.KMS_KEY_ID)
    )
    artifact_type: ArtifactType = Field(default_factory=get_artifact_type)
    connector_token: Optional[str] = Field(
        default_factory=lambda: os.environ.get(EnvVars.CONNECTOR_TOKEN),
        description="User provided authentication token",
    )
    local_certificate_file: str = Field(
        default_factory=lambda: os.environ.get(EnvVars.LOCAL_CERTIFICATE_PEM_LOCATION)
        or DEFAULT_LOCAL_CERTIFICATE_FILE
    )
    skip_cloudwatch: bool = Field(
        default_factory=lambda: os.environ.get(EnvVars.SKIP_CLOUDWATCH) == "true"
    )
