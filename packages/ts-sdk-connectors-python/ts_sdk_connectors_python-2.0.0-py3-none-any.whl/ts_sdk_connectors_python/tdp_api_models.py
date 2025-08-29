"""
TDP API models for the TS SDK Connectors Python.

This module re-exports all OpenAPI-generated model classes from their original location,
making them easier to import and use.

Instead of:
    from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.models.connector_details_dto import ConnectorDetailsDto
    or
    from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.models import ConnectorDetailsDto

You can now use:
    from ts_sdk_connectors_python.tdp_api_models import ConnectorDetailsDto
"""

from typing import List

from pydantic import BaseModel, Field

from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.models import *  # noqa: F401
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.models import (  # noqa: F401
    __all__,
)


class CertificateDto(BaseModel):
    """
    Certificate data model for the TDP certificates endpoint.

    Attributes:
        id: Unique identifier for the certificate
        name: Name of the certificate
        org_slug: Organization slug the certificate belongs to
        content: The certificate content in PEM format
        disabled: Whether the certificate is disabled
        created_at: Creation timestamp
        last_updated_at: Last update timestamp
        valid_from: Validity start timestamp
        expires_at: Expiration timestamp
    """

    id: str
    name: str
    org_slug: str = Field(..., alias="orgSlug")
    content: str
    disabled: bool
    created_at: str = Field(..., alias="createdAt")
    last_updated_at: str = Field(..., alias="lastUpdatedAt")
    valid_from: str = Field(..., alias="validFrom")
    expires_at: str = Field(..., alias="expiresAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True


class GetCertificatesResponse(BaseModel):
    """
    Response model for the certificates endpoint.

    In the Node SDK, this is an array of CertificateDto objects.
    """

    certificates: List[CertificateDto] = []

    @classmethod
    def from_list(cls, certificates_list: List[dict]) -> "GetCertificatesResponse":
        """
        Create a GetCertificatesResponse from a list of certificate dictionaries.

        Args:
            certificates_list: List of certificate dictionaries

        Returns:
            GetCertificatesResponse object
        """
        return cls(certificates=[CertificateDto(**cert) for cert in certificates_list])
