# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["IngestionResponse"]


class IngestionResponse(BaseModel):
    id: str
    """ID of the document being ingested"""
