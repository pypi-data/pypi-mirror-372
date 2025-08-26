from __future__ import annotations

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIWrapper(BaseModel, Generic[T]):
    Code: int
    Msg: Optional[str] = None
    Data: Optional[T]
