"""
This module provides utilities for working with Pydantic JSON types and event handling.

Exports:
    - PydanticJSON: A custom SQLAlchemy type for handling Pydantic models as JSON.
    - flag_pydantic_changes: A utility function to flag changes in Pydantic models. Needs to be set as an event for SQLAlchemy.
"""

from .type import PydanticJSON
from .event import flag_pydantic_changes

__all__ = ["PydanticJSON", "flag_pydantic_changes"]
