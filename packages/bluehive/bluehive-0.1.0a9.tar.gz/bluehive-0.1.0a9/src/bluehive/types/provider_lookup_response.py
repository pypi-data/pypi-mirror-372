# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["ProviderLookupResponse", "Provider"]


class Provider(BaseModel):
    address_1: str
    """Primary address line"""

    address_2: str
    """Secondary address line (suite, unit, etc.)"""

    city: str
    """City"""

    country: str
    """Country code"""

    distance: float
    """Distance in miles from the provided ZIP code"""

    fax_number: str
    """Fax number"""

    firstname: str
    """Provider first name"""

    lastname: str
    """Provider last name or organization name"""

    npi: str
    """National Provider Identifier (NPI) number"""

    postal_code: str
    """Postal/ZIP code"""

    state_province: str
    """State or province code"""

    work_phone: str
    """Work phone number"""


class ProviderLookupResponse(BaseModel):
    count: float
    """Number of providers found"""

    providers: List[Provider]
    """List of matching providers"""
