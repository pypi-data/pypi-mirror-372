# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DatabaseCheckHealthResponse", "Stats"]


class Stats(BaseModel):
    collections: Optional[float] = None
    """Number of collections"""

    data_size: Optional[float] = FieldInfo(alias="dataSize", default=None)
    """Total data size in bytes"""

    documents: Optional[float] = None
    """Total number of documents"""


class DatabaseCheckHealthResponse(BaseModel):
    status: Literal["ok", "error"]
    """Database health status"""

    timestamp: str
    """Health check timestamp"""

    database: Optional[str] = None
    """Database name (hidden in production)"""

    error: Optional[str] = None
    """Error message if status is error"""

    stats: Optional[Stats] = None
    """Database statistics (not available in production)"""
