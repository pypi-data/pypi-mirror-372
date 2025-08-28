from typing import List, TypeVar, Generic, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar('T')

class Category(BaseModel):
    id: str
    is_service: bool = Field(..., alias='isService')
    name: str
    parent_category_id: str = Field(..., alias='parentCategoryId')

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    lower_bound: int = Field(..., alias='lowerBound')
    page_no: int = Field(..., alias='pageNo')
    total_count: int = Field(..., alias='totalCount')
    total_pages: int = Field(..., alias='totalPages')
    upper_bound: int = Field(..., alias='upperBound')

class APIResponse(BaseModel, Generic[T]):
    error: Optional[Any]
    result: Optional[T]
    success: bool
    un_authorized_request: bool = Field(..., alias='unAuthorizedRequest')
