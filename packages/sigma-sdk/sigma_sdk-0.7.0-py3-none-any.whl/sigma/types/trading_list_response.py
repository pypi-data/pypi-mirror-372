# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .order import Order

__all__ = ["TradingListResponse"]

TradingListResponse: TypeAlias = List[Order]
