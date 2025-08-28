# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Instrument"]


class Instrument(BaseModel):
    base_asset: Optional[str] = FieldInfo(alias="baseAsset", default=None)

    quote_asset: Optional[str] = FieldInfo(alias="quoteAsset", default=None)

    symbol: Optional[str] = None
