# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Order"]


class Order(BaseModel):
    order_id: Optional[str] = FieldInfo(alias="orderId", default=None)

    price: Optional[str] = None

    quantity: Optional[str] = None

    side: Optional[Literal["buy", "sell"]] = None

    symbol: Optional[str] = None

    type: Optional[Literal["market", "limit"]] = None
