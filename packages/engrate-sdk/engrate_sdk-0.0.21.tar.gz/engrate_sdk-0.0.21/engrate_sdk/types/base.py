"""Type definitions for Engrate SDK.

This module provides type aliases and constraints for identifiers used throughout the SDK.
"""

from typing import Annotated

from pydantic import StringConstraints

IDENTIFIER_RE = r"^[A-Za-z0-9_.-]{1,64}$"
Identifier = Annotated[str, StringConstraints(pattern=IDENTIFIER_RE)]
