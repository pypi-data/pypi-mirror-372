# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ProviderLookupParams"]


class ProviderLookupParams(TypedDict, total=False):
    firstname: str
    """Provider first name"""

    lastname: str
    """Provider last name"""

    npi: str
    """Provider NPI number"""

    zipcode: str
    """ZIP code to filter results by proximity"""
