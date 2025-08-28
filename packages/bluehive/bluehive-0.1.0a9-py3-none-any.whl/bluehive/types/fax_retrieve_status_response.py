# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["FaxRetrieveStatusResponse"]


class FaxRetrieveStatusResponse(BaseModel):
    id: str
    """Fax identifier"""

    created_at: str = FieldInfo(alias="createdAt")
    """ISO timestamp when fax was created"""

    from_: str = FieldInfo(alias="from")
    """Sender fax number"""

    provider: str
    """Provider used to send the fax"""

    status: Literal["queued", "dialing", "sending", "delivered", "failed", "cancelled", "retrying"]
    """Current fax status"""

    to: str
    """Recipient fax number"""

    updated_at: str = FieldInfo(alias="updatedAt")
    """ISO timestamp when status was last updated"""

    cost: Optional[float] = None
    """Cost of the fax"""

    delivered_at: Optional[str] = FieldInfo(alias="deliveredAt", default=None)
    """ISO timestamp when fax was delivered"""

    duration: Optional[float] = None
    """Call duration in seconds"""

    error_message: Optional[str] = FieldInfo(alias="errorMessage", default=None)
    """Error message if fax failed"""

    page_count: Optional[float] = FieldInfo(alias="pageCount", default=None)
    """Number of pages in the fax"""

    provider_data: Optional[object] = FieldInfo(alias="providerData", default=None)
    """Provider-specific additional data"""
