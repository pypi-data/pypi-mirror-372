# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["OpenPosition"]


class OpenPosition(BaseModel):
    entry_price: Optional[str] = FieldInfo(alias="entryPrice", default=None)

    position_amt: Optional[str] = FieldInfo(alias="positionAmt", default=None)

    symbol: Optional[str] = None
