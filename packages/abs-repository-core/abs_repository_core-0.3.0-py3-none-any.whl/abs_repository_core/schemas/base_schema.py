from datetime import datetime
from typing import Any, List, Optional, Literal, Union, Dict, Annotated
from uuid import UUID

from pydantic import BaseModel, Field

class ModelBaseInfo(BaseModel):
    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class DraftModelBaseInfo(ModelBaseInfo):
    is_draft: bool = True

# Primitive field condition
class FieldOperatorCondition(BaseModel):
    field: str
    operator: Literal["eq", "neq", "gt", "gte", "lt", "lte", "in", "not_in", "like", "ilike", "between", "is_null", "is_not_null"]
    value: Any

    model_config = {
        "from_attributes": True
    }

# Base structure for a logical group
class LogicalCondition(BaseModel):
    operator: Literal["AND", "OR"]
    conditions: List["ConditionType"]

    model_config = {
        "from_attributes": True
    }

# Each item in conditions list can be:
# 1. a logical condition (nested group)
# 2. a dict like {field: ..., operator: ..., value: ...}
ConditionType = Union["LogicalCondition", "FieldOperatorCondition"]

# Top-level filter schema
class FilterSchema(BaseModel):
    operator: Literal["AND", "OR"]
    conditions: List[ConditionType]

    model_config = {
        "from_attributes": True
    }

# Sort schema
class SortOrder(BaseModel):
    field: str
    direction: Literal["asc", "desc"]

    model_config = {
        "from_attributes": True
    }

# Base schema for find operations
class FindBase(BaseModel):
    sort_orders: Optional[List[SortOrder]] = None
    page: Optional[int] = 1
    page_size: Optional[int] = 10
    search: Optional[str] = None
    filters: Optional[FilterSchema] = None
    searchable_fields: Optional[List[str]] = None

    model_config = {
        "from_attributes": True
    }

# Schema for displaying search operations
class SearchOptions(FindBase):
    total_count: Optional[int] = None
    total_pages: Optional[int] = None

# Schema for displaying find operation's result
class FindResult(BaseModel):
    founds: Optional[List] = None
    search_options: Optional[SearchOptions] = None

    model_config = {
        "from_attributes": True
    }

# Schema for getting distinct values of a field
class FindUniqueValues(BaseModel):
    field_name: str
    ordering: Optional[Literal["asc", "desc"]] = None
    page: Optional[int] = 1
    page_size: Optional[int] = 10
    search: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

# Schema for displaying distinct values of a field
class UniqueValuesResult(BaseModel):
    founds: List[Any]
    search_options: Optional[SearchOptions] = None

    model_config = {
        "from_attributes": True
    }
