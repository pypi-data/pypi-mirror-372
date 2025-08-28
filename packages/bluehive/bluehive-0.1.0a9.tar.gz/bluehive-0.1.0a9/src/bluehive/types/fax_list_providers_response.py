# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["FaxListProvidersResponse", "Provider"]


class Provider(BaseModel):
    configured: bool
    """Whether the provider is properly configured"""

    is_default: bool = FieldInfo(alias="isDefault")
    """Whether this is the default provider"""

    name: str
    """Provider name"""


class FaxListProvidersResponse(BaseModel):
    providers: List[Provider]
