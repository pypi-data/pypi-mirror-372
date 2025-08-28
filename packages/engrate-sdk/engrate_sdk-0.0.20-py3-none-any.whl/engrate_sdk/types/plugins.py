"""Types and base classes for plugins in the Engrate SDK.

This module defines the BasePlugin class and related types for plugin development.
"""

from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, computed_field

from engrate_sdk.utils import log

log = log.get_logger(__name__)

class ProductCategory(str, Enum):
    """Enum for product categories."""

    BILLING = "billing"
    CONTROLLING = "controlling"
    FORECAST = "forecast"
    MARKET_INTELLIGENCE = "market_intelligence"
    METERING = "metering"
    OPTIMIZATION = "optimization"
    SCHEDULING = "scheduling"
    SETTLEMENT = "settlement"
    STRUCTURING = "structuring"
    TRADING = "trading"


class PluginSpec(BaseModel):
    uid:UUID | None = None
    name: str
    author:str
    description: str | None  = None
    product_category: ProductCategory
    enabled:bool = False
    extensions:dict[str,Any] = {}
    plugin_metadata:dict[str,Any] = {} # Metadata is a reserved word, is not worth to try to use it as a field name (possible though)

    def service_name(self) -> str | None:
        """Get the URI path of the plugin."""
        return self.plugin_metadata.get("service_name", None)

    def port(self) -> str | None:
        """Get the port of the plugin."""
        return self.plugin_metadata.get("port", None)

    def api_version(self) -> str | None:
        """Get the port of the plugin."""
        return self.plugin_metadata.get("api_version", None)

    @computed_field
    @property
    def doc_url(self)-> str:
        return f"{self.api_version()}/plugins/{self.service_name()}/openapi.json"


class PluginsDetailsSpec(PluginSpec):
    purchased: bool = False

class PluginsOrgSettingsSpec(BaseModel):
    org_uid: UUID
    plugin_uid: UUID
    settings: dict[str,str] = []
