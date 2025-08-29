import os
import ssl
from typing import Optional

import aiobotocore
import aiobotocore.client
import certifi
from botocore.exceptions import ClientError
from pydantic import BaseModel

from ts_sdk_connectors_python.aws import AWS
from ts_sdk_connectors_python.constants import EnvVars
from ts_sdk_connectors_python.logger._base import CloudWatchLoggingAdapter, get_logger

logger = get_logger(__name__)


class CertConfig(BaseModel):
    local_cert_file: Optional[str] = None
    stream_bucket: Optional[str] = None
    tdp_certificate_key: Optional[str] = None


async def load_tdp_certificates_from_s3(
    s3_client: aiobotocore.client.AioBaseClient,
    logger: CloudWatchLoggingAdapter,
    config: CertConfig,
):
    bucket = config.stream_bucket
    tdp_cert_key = config.tdp_certificate_key

    if not bucket:
        logger.info("stream_bucket config not set; skipping TDP certificate retrieval")
        return []

    if not tdp_cert_key:
        logger.info(
            "tdp_certificate_key config not set; skipping TDP certificate retrieval"
        )
        return []

    logger.info(
        f"Retrieving TDP certificates from AWS S3, key: {tdp_cert_key}, bucket: {bucket}",
    )

    try:
        response = await s3_client.get_object(Bucket=bucket, Key=tdp_cert_key)
        cert = await response["Body"].read()
        cert = cert.decode("utf-8")
        if not cert:
            logger.warning(
                "Failed to load TDP certificates from S3, undefined response"
            )
            return []

        logger.info("Found TDP certificate in S3")
        return [cert]
    except ClientError as client_err:
        if "specified key does not exist" in str(client_err):
            logger.warning(f"Did not find TDP certificate in S3: {client_err}")
        else:
            logger.error(f"Error retrieving TDP certificates from S3: {client_err}")
        return []


def load_certificates_from_local_volume(
    config: CertConfig, logger: CloudWatchLoggingAdapter
) -> list[str]:
    local_cert_file = config.local_cert_file

    if not local_cert_file:
        logger.debug("local_cert_file config not set; skipping local certificate load")
        return []

    if not os.path.exists(local_cert_file):
        logger.debug(f"Local TDP certificate file does not exist at {local_cert_file}")
        return []

    try:
        logger.debug(f"Loading TDP certificates from local volume {local_cert_file}")
        with open(local_cert_file, "r", encoding="utf-8") as file:
            cert = file.read()

        if not cert:
            logger.warning(f"The certificate file {local_cert_file} is empty")
            return []

        logger.info(f"TDP certificates loaded from local volume {local_cert_file}")
        return [cert]

    except Exception as ex:
        logger.error(
            f"Error loading TDP certificates from local volume {local_cert_file}: {ex}",
        )
        return []


def load_httpx_default_certificates() -> str:
    """
    The default certificates are explicitly loaded with the certify package.
    This package contains Mozilla's curated collection of CA certificates, and
    also includes the Amazon Trust CA certs used by TDP
    """
    default_cert_path = certifi.where()

    with open(default_cert_path, "r") as default_cert_file:
        return default_cert_file.read()


async def create_combined_ssl_context(
    aws: AWS, logger: CloudWatchLoggingAdapter, config: CertConfig
) -> ssl.SSLContext:
    """
    Create an SSL context for httpx with TDP certificates and Certifi/mozilla CA certificates.
    The certificates (via `certifi`) may differ from those used by `ssl.create_default_context()`,
    which can be from the OS CA store.
    """
    context = ssl.create_default_context()
    if os.getenv(EnvVars.CONNECTOR_TOKEN):
        # standalone connectors have certificates in local volume
        certificates = load_certificates_from_local_volume(config, logger)
    elif aws and config.stream_bucket and config.tdp_certificate_key:
        # This is a tetra cloud or hub hosted connector with certificates in S3
        async with await aws.create_client("s3") as s3_client:
            certificates = await load_tdp_certificates_from_s3(
                s3_client, logger, config
            )
    else:
        raise RuntimeError(
            "Unable to create SSL context: no certificates found. "
            f"To load certificates locally, set the environment variable '{EnvVars.CONNECTOR_TOKEN}'. "
            f"To load certificates from S3, ensure both '{EnvVars.STREAM_BUCKET}' and '{EnvVars.TDP_CERTIFICATE_KEY}' are configured. "
            "Make sure these environment variables are correctly set in your deployment configuration."
        )

    certificates.append(load_httpx_default_certificates())
    for cert in certificates:
        context.load_verify_locations(cadata=cert)

    return context
