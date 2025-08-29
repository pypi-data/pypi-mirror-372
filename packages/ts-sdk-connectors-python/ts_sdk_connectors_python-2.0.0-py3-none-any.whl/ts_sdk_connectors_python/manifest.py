import os

from pydantic import BaseModel, ConfigDict

from ts_sdk_connectors_python import get_logger

logger = get_logger(__name__)


class ConnectorManifest(BaseModel):
    """
    ConnectorManifest is a model representing the manifest of a connector.

    Attributes:
        type (str): The type of the connector.
        slug (str): The slug identifier for the connector.
        namespace (str): The namespace of the connector.
        version (str): The version of the connector.
        description (str): A brief description of the connector.
    """

    model_config = ConfigDict(extra="ignore")

    type: str
    slug: str
    namespace: str
    version: str
    description: str


def get_connector_manifest() -> ConnectorManifest | None:
    """
    Gets the manifest.json file from the current working directory.
    In a running connector, this ought to be next to main.py.
    Returns `None` if no `manifest.json` is found.
    """
    manifest_path = os.path.abspath("manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path) as manifest_file:
            try:
                return ConnectorManifest.model_validate_json(manifest_file.read())
            except Exception as e:
                logger.error(
                    f"Error reading connector manifest.json: {str(e)}",
                    exc_info=True,
                    extra={"path": manifest_path},
                )
    return None
