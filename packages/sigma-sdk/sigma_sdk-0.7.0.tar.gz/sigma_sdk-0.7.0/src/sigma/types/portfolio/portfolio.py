# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .balance import Balance
from ..._models import BaseModel

__all__ = ["Portfolio"]


class Portfolio(BaseModel):
    assets: Optional[List[Balance]] = None
