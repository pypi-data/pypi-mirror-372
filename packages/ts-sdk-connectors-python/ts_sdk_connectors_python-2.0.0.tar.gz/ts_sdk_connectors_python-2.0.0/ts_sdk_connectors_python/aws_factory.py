import asyncio
import os
import threading
from typing import Dict, Optional, Tuple

from ts_sdk_connectors_python.aws import AWS
from ts_sdk_connectors_python.certificate import CertConfig
from ts_sdk_connectors_python.client_creator import AuthenticatedClientCreator
from ts_sdk_connectors_python.constants import EnvVars
from ts_sdk_connectors_python.logger._base import (  # Import directly from modules to avoid circular references
    get_logger,
)
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.client import (
    AuthenticatedClient,
)

logger = get_logger(__name__)


class AWSFactory:
    """
    Singleton for creating thread-safe and event-loop-safe AWS instances via .get_aws_instance(...)

    This class ensures that each thread and asyncio event loop gets its own
    dedicated AWS instance to prevent concurrency issues.
    """

    _instance = None
    _rlock = threading.RLock()
    _instances: Dict[Tuple[int, int], AWS] = {}
    _loop_ids: Dict[int, asyncio.AbstractEventLoop] = {}

    def __new__(cls):
        with cls._rlock:
            if cls._instance is None:
                cls._instance = super(AWSFactory, cls).__new__(cls)
                cls._instance._instances = {}
                cls._instance._loop_ids = {}
            return cls._instance

    def __init__(self):
        pass

    async def get_aws_instance(
        self,
        connector_id: Optional[str],
        org_slug: Optional[str],
        http_client: Optional[AuthenticatedClient] = None,
        aws_region: Optional[str] = None,
    ) -> AWS:
        """
        Get or create an AWS instance specific to the current thread and event loop.

        Args:
            connector_id: The connector ID
            org_slug: The organization slug
            http_client: Optional authenticated client
            token: Optional authentication token
            aws_region: Optional AWS region

        Returns:
            An AWS instance specific to the current thread and event loop
        """
        thread_id = threading.get_ident()

        try:
            loop = asyncio.get_running_loop()
            loop_id = id(loop)
            # Store loop reference to prevent garbage collection
            self._loop_ids[loop_id] = loop
        except RuntimeError:
            # No event loop running
            loop_id = 0

        instance_key = (thread_id, loop_id)

        with self._rlock:
            if instance_key not in self._instances:
                logger.debug(
                    f"Creating new AWS instance for thread {thread_id}, loop {loop_id}",
                    extra={"thread_id": thread_id, "loop_id": loop_id},
                )

                # If no http_client is provided and we're in standalone mode, create the AuthenticatedClient
                # in order to fetch AWS credentials from TDP
                if http_client is None and os.getenv(EnvVars.CONNECTOR_TOKEN):
                    tdp_endpoint = os.environ.get(EnvVars.TDP_ENDPOINT)
                    assert (
                        tdp_endpoint
                    ), "TDP_ENDPOINT is not set in environment variables"

                    disable_verify = (
                        True
                        if os.environ.get(EnvVars.TDP_TLS_REJECT_UNAUTHORIZED)
                        else False
                    )

                    client_creator = AuthenticatedClientCreator(
                        base_url=tdp_endpoint,
                        cert_config=CertConfig(
                            local_cert_file=os.environ.get(
                                EnvVars.LOCAL_CERTIFICATE_PEM_LOCATION
                            ),
                            stream_bucket=os.environ.get(EnvVars.STREAM_BUCKET),
                            tdp_certificate_key=os.environ.get(
                                EnvVars.TDP_CERTIFICATE_KEY
                            ),
                        ),
                        disable_verify=disable_verify,
                    )

                    http_client = await client_creator.create()
                    logger.debug(
                        f"Created authenticated client for TDP endpoint: {tdp_endpoint}"
                    )

                aws_logger = self.create_aws_logger("aws")
                aws_instance = AWS(
                    connector_id=connector_id,
                    org_slug=org_slug,
                    http_client=http_client,
                    aws_region=aws_region,
                    logger=aws_logger,
                )

                self._instances[instance_key] = aws_instance

            return self._instances[instance_key]

    def create_aws_logger(self, base_name):
        """Create a child logger with thread and event loop context"""
        thread_id = threading.get_ident()

        try:
            loop = asyncio.get_running_loop()
            loop_id = id(loop)
        except RuntimeError:
            loop_id = 0

        extra = {"thread_id": thread_id, "loop_id": loop_id}

        return get_logger(f"{base_name}.{thread_id}.{loop_id}", extra=extra)

    def clear_aws_instance(self):
        """
        Clear the AWS instance for the current thread and event loop.
        Useful for testing or when resources need to be explicitly cleaned up.
        """
        thread_id = threading.get_ident()

        try:
            loop = asyncio.get_running_loop()
            loop_id = id(loop)
        except RuntimeError:
            loop_id = 0

        instance_key = (thread_id, loop_id)

        with self._rlock:
            if instance_key in self._instances:
                del self._instances[instance_key]

    def clear_all_instances(self):
        """Clear all AWS instances across all threads and event loops."""
        with self._rlock:
            self._instances.clear()
            self._loop_ids.clear()
