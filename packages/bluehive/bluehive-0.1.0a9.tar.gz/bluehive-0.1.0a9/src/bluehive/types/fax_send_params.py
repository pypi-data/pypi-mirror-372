# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["FaxSendParams", "Document"]


class FaxSendParams(TypedDict, total=False):
    document: Required[Document]

    to: Required[str]
    """Recipient fax number (E.164 format preferred)"""

    from_: Annotated[str, PropertyInfo(alias="from")]
    """Sender fax number (optional, uses default if not provided)"""

    provider: str
    """Optional provider override (uses default if not specified)"""

    subject: str
    """Subject line for the fax"""


class Document(TypedDict, total=False):
    content: Required[str]
    """Base64 encoded document content"""

    content_type: Required[
        Annotated[
            Literal["application/pdf", "image/tiff", "image/tif", "image/jpeg", "image/jpg", "image/png", "text/plain"],
            PropertyInfo(alias="contentType"),
        ]
    ]
    """MIME type of the document"""

    filename: str
    """Optional filename for the document"""
