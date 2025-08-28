"""Plugin registry module for the Engrate SDK.

This module provides the PluginRegistry class for managing plugin registration
with a remote registrar service.
At the moment, this method is proactive (the client is responsible for
registering plugins), but this will change in the future to a more
reactive approach where the server will automatically discover and register
plugins.
"""

from http import HTTPStatus
from pathlib import Path

from engrate_sdk.http.client import AsyncClient
from engrate_sdk.types.exceptions import (
    ParseError,
    UncontrolledError,
    ValidationError,
    AlreadyExistsError,
)
from engrate_sdk.types.plugins import PluginSpec
from engrate_sdk.utils import log

logger = log.get_logger(__name__)


class PluginRegistry:
    """A registry for managing plugins in the Engrate SDK."""

    def __init__(self, registrar_url: str, manifest_path: str | None = None):
        """Initialize the plugin registry."""
        self.registrar_url = registrar_url
        self.manifest_path = manifest_path

    def __load_yaml(self) -> PluginSpec:
        """Load the plugin specification from a YAML file.

        TODO this should be in a module
        """
        import yaml

        try:
            manifest_path = (
                Path(self.manifest_path)
                if self.manifest_path
                else Path("plugin_manifest.yaml")
            )
            logger.info(f"Attempt to load plugin specification from {manifest_path}")
            with manifest_path.open() as file:
                data = yaml.safe_load(file)
                logger.info("Plugin specification loaded successfully.")
                return PluginSpec(**data)
        except FileNotFoundError as err:
            raise ValidationError("Plugin specification file not found.") from err
        except yaml.YAMLError as err:
            raise ParseError(f"Error parsing plugin specification: {err}") from err

    async def register_plugin(self):
        """Register a plugin in the registry."""
        try:
            plugin = self.__load_yaml()

            async with AsyncClient() as client:
                response = await client.post(
                    url=self.registrar_url,
                    json=plugin.model_dump(),
                    headers={"Content-Type": "application/json"},
                )
                if response.status_code != HTTPStatus.CREATED:
                    json = response.json()
                    msg = json.get("message", "Unknown error")
                    if HTTPStatus.CONFLICT:
                        logger.warning(
                            f"Plugin {plugin.name} is already registered, skipping registration."
                        )
                        raise AlreadyExistsError(kind="plugin", id=plugin.name)
                    raise UncontrolledError(f"Failed to register plugin: {msg}")
        except Exception as e:
            logger.error(f"Error registering plugin: {e}")
            raise
