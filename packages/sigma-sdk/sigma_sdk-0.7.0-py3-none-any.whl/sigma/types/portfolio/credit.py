# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Credit"]


class Credit(BaseModel):
    credit_line: Optional[str] = FieldInfo(alias="creditLine", default=None)

    used_credit: Optional[str] = FieldInfo(alias="usedCredit", default=None)
