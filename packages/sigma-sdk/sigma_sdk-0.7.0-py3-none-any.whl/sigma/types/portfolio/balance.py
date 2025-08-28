# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["Balance"]


class Balance(BaseModel):
    asset: Optional[str] = None

    free: Optional[str] = None

    locked: Optional[str] = None
