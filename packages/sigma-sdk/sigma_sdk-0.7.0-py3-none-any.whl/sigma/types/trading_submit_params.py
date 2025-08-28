# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TradingSubmitParams"]


class TradingSubmitParams(TypedDict, total=False):
    order_id: Annotated[str, PropertyInfo(alias="orderId")]

    price: str

    quantity: str

    side: Literal["buy", "sell"]

    symbol: str

    type: Literal["market", "limit"]
