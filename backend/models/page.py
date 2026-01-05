from typing import Generic, List, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    content: List[T]
    page: int
    size: int
    totalElements: int
    totalPages: int
