from contextlib import AbstractContextManager
from typing import Any, Callable, List, Optional, Type, TypeVar, Union, Dict
from enum import Enum

from fastapi import HTTPException
from sqlalchemy import distinct, func, or_, and_, desc, asc, not_, between
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload,class_mapper,aliased
from sqlalchemy.sql import expression
from ..utils.get_field import get_field
from abs_exception_core.exceptions import (
    DuplicatedError,
    NotFoundError,
    ValidationError
)
from ..models import BaseModel
from ..schemas import FindBase, SortOrder, FindUniqueValues
T = TypeVar("T", bound=BaseModel)

# Default values for pagination and ordering
DEFAULT_ORDERING:str = "asc"
DEFAULT_PAGE:int = 1
DEFAULT_PAGE_SIZE:int = 20

class FilterOperator(str, Enum):
    AND = "and"
    OR = "or"

class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"

class ComparisonOperator(str, Enum):
    EQ = "eq"  # equals
    NE = "neq"  # not equals
    GT = "gt"  # greater than
    GTE = "gte"  # greater than or equal
    LT = "lt"  # less than
    LTE = "lte"  # less than or equal
    LIKE = "like"  # like
    ILIKE = "ilike"  # case-insensitive like
    IN = "in"  # in list
    NOT_IN = "not_in"  # not in list
    BETWEEN = "between"  # between two values
    IS_NULL = "is_null"  # is null
    IS_NOT_NULL = "is_not_null"  # is not null

class BaseRepository:
    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
        model: Type[T],
    ) -> None:
        self.session_factory = session_factory
        self.model = model

    def _apply_comparison_operator(self, field: str, operator: ComparisonOperator, value: Any) -> expression.BinaryExpression:
        
        if operator == ComparisonOperator.EQ:
            return field == value
        elif operator == ComparisonOperator.NE:
            return field != value
        elif operator == ComparisonOperator.GT:
            return field > value
        elif operator == ComparisonOperator.GTE:
            return field >= value
        elif operator == ComparisonOperator.LT:
            return field < value
        elif operator == ComparisonOperator.LTE:
            return field <= value
        elif operator == ComparisonOperator.LIKE:
            return field.like(f"%{value}%")
        elif operator == ComparisonOperator.ILIKE:
            return field.ilike(f"%{value}%")
        elif operator == ComparisonOperator.IN:
            return field.in_(value if isinstance(value, list) else [value])
        elif operator == ComparisonOperator.NOT_IN:
            return ~field.in_(value if isinstance(value, list) else [value])
        elif operator == ComparisonOperator.BETWEEN:
            if not isinstance(value, list) or len(value) != 2:
                raise ValidationError(detail="BETWEEN operator requires a list with exactly 2 values")
            return between(field, value[0], value[1])
        elif operator == ComparisonOperator.IS_NULL:
            return field.is_(None)
        elif operator == ComparisonOperator.IS_NOT_NULL:
            return field.isnot(None)
        else:
            raise ValidationError(detail=f"Unsupported comparison operator: {operator}")

    def _build_filter_conditions(self, filter_dict: Dict,query) -> Any:
        conditions = []
        
        if not isinstance(filter_dict, dict):
            return conditions
        
        # Handle operator and conditions structure
        if "operator" in filter_dict and "conditions" in filter_dict:
            nested_conditions = []
            try:
                current_operator = FilterOperator(filter_dict["operator"].lower())
            except ValueError:
                raise ValidationError(detail=f"Invalid operator: {filter_dict['operator']}. Must be one of: {', '.join(op.value for op in FilterOperator)}")
            
            # Process each condition in the list
            for condition in filter_dict["conditions"]:
                if isinstance(condition, dict):
                    # Handle nested operator/conditions
                    if "operator" in condition and "conditions" in condition:
                        query,nested_result = self._build_filter_conditions(condition,query)
                        if nested_result:
                            nested_conditions.extend(nested_result)

                    # Handle comparison operators
                    elif "field" in condition and "operator" in condition and "value" in condition:
                        try:
                            # Convert comparison operator to lowercase before creating enum
                            comparison_op = ComparisonOperator(condition["operator"].lower())
                            query,field_name = get_field(self.model,condition["field"],query)
                            nested_conditions.append(
                                self._apply_comparison_operator(field_name, comparison_op, condition["value"])
                            )
                        except ValueError:
                            raise ValidationError(detail=f"Invalid comparison operator: {condition['operator']}. Must be one of: {', '.join(op.value for op in ComparisonOperator)}")
                    else:
                        raise ValidationError(detail=f"Invalid condition: {condition}")
            
            # Combine all conditions with the specified operator
            if nested_conditions:
                conditions.append(
                    and_(*nested_conditions) if current_operator == FilterOperator.AND 
                    else or_(*nested_conditions)
                )
        
        return query,conditions

    def _build_sort_orders(self, sort_orders: List[SortOrder],query) -> Any:
        orders = []
        for sort in sort_orders:
            field = sort.get("field")
            direction = sort.get("direction", SortDirection.ASC)

            if "." in field:
                query, column = get_field(self.model, field, query)
            else:
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                else:
                    raise ValidationError(detail=f"Field '{field}' does not exist on model {self.model.__name__}")

            # Append the appropriate ordering direction
            if direction == SortDirection.DESC:
                orders.append(desc(column))
            else:
                orders.append(asc(column))

        return query, orders
    

    def build_nested_search(self, search_fields:List[str],search_term:str,query):
        search_conditions = []
        for field in search_fields:
            if "." in field:
                query,field_name = get_field(self.model,field,query)
                condition = field_name.ilike(f"%{search_term}%")
                search_conditions.append(condition)
            else:
                if hasattr(self.model, field):
                    condition = getattr(self.model, field).ilike(f"%{search_term}%")
                    search_conditions.append(condition)

        if search_conditions:
            return query, or_(*search_conditions)
        return query,None

    def read_by_options(
        self,
        schema: FindBase,
        eager: bool = True,
    ) -> dict:
        with self.session_factory() as session:
            try:
                schema_as_dict: dict = schema.model_dump(exclude_unset=False)

                searchable_fields = schema_as_dict.get("searchable_fields")
                if isinstance(searchable_fields, str):
                    searchable_fields = [searchable_fields]

                page = schema_as_dict.get("page") or DEFAULT_PAGE
                page_size = schema_as_dict.get("page_size") or DEFAULT_PAGE_SIZE
                search_term = schema_as_dict.get("search") or None
                query = session.query(self.model)

                # Handle eager loading
                if eager:
                    for relation_path in getattr(self.model, "eagers", []):
                        path_parts = relation_path.split(".")
                        current_class = self.model
                        current_attr = getattr(current_class, path_parts[0])
                        loader = joinedload(current_attr)

                        for part in path_parts[1:]:
                            current_class = current_attr.property.mapper.class_
                            current_attr = getattr(current_class, part)
                            loader = loader.joinedload(current_attr)

                        query = query.options(loader)

                # Handle complex filters
                filter_dict = schema_as_dict.get("filters", {})
                if filter_dict:
                    query,filter_conditions = self._build_filter_conditions(filter_dict,query)
                    
                    if filter_conditions:
                        query = query.filter(and_(*filter_conditions))

                # Handle search with related fields
                if searchable_fields and search_term:
                    query,search_query = self.build_nested_search(search_fields=searchable_fields,search_term=search_term,query=query)
                    query = query.filter(search_query)

                # Apply multiple sorting
                sort_orders = schema_as_dict.get("sort_orders", [])
                if sort_orders and len(sort_orders) > 0:
                    query,sort_query = self._build_sort_orders(sort_orders,query)
                    query = query.order_by(*sort_query)
                else:
                    query = query.order_by(self.model.id.desc())

                total_count = query.count()

                # Apply pagination
                if page_size == "all":
                    results = query.all()
                else:
                    results = (
                        query.limit(page_size).offset((page - 1) * page_size).all()
                    )

                # Calculate the total number of pages
                total_pages = (total_count + page_size - 1) // page_size

                return {
                    "founds": results,
                    "search_options": {
                        "page": page,
                        "page_size": page_size,
                        "search": search_term,
                        "total_count": total_count,
                        "total_pages": total_pages,
                    },
                }
            except SQLAlchemyError as e:
                raise ValidationError(detail=str(e))

    def read_by_id(self, id: int, eager: bool = False):
        with self.session_factory() as session:
            try:
                query = session.query(self.model)

                # Handle eager loading
                if eager:
                    for relation_path in getattr(self.model, "eagers", []):
                        path_parts = relation_path.split(".")
                        current_class = self.model
                        current_attr = getattr(current_class, path_parts[0])
                        loader = joinedload(current_attr)

                        for part in path_parts[1:]:
                            current_class = current_attr.property.mapper.class_
                            current_attr = getattr(current_class, part)
                            loader = loader.joinedload(current_attr)

                        query = query.options(loader)
                query = query.filter(self.model.id == id).first()
                if not query:
                    raise NotFoundError(detail=f"Record not found with id: {id}")
                return query
            except SQLAlchemyError as e:
                raise e

    def read_by_attr(self, attr: str,value:Any, eager: bool = False):
        with self.session_factory() as session:
            try:
                query = session.query(self.model)
                if not hasattr(self.model, attr):
                    raise NotFoundError(detail=f"Field '{attr}' does not exist on model {self.model.__name__}")
                
                # Handle eager loading
                if eager:
                    for relation_path in getattr(self.model, "eagers", []):
                        path_parts = relation_path.split(".")
                        current_class = self.model
                        current_attr = getattr(current_class, path_parts[0])
                        loader = joinedload(current_attr)

                        for part in path_parts[1:]:
                            current_class = current_attr.property.mapper.class_
                            current_attr = getattr(current_class, part)
                            loader = loader.joinedload(current_attr)

                        query = query.options(loader)
                query = query.filter(getattr(self.model, attr) == value).first()

                if not query:
                    raise NotFoundError(detail=f"Requested {attr} : {value} does not exist.")
                return query
            except SQLAlchemyError as e:
                raise e
            except NotFoundError as e:
                raise e

    def create(self, schema: T):
        with self.session_factory() as session:
            try:
                session.add(schema)
                session.commit()
                session.refresh(schema)
                query = self.read_by_id(schema.id, eager=True)
            except IntegrityError as e:
                raise DuplicatedError(detail=str(e.orig))
            except SQLAlchemyError as e:
                raise e
            return query

    def bulk_create(self, schemas: List[T]):
        with self.session_factory() as session:
            try:
                session.bulk_insert_mappings(self.model, schemas)
                session.commit()
                session.refresh(schemas)
            except SQLAlchemyError as e:
                raise e
            
            return schemas
        
    def update(self, id: int, schema: T):
        with self.session_factory() as session:
            try:
                # Apply updates
                affected_rows = (
                    session.query(self.model)
                    .filter(self.model.id == id)
                    .update(
                        schema.model_dump(exclude_none=True),
                        synchronize_session="fetch",
                    )
                )
                if not affected_rows:
                    raise NotFoundError(detail="Requested record does not exist.")
                session.commit()

                query = self.read_by_id(id, eager=True)

                return query 

            except SQLAlchemyError as e:
                raise e
            except NotFoundError as e:
                raise e
            
    def update_attr(self, id: int, column: str, value: Any):
        with self.session_factory() as session:
            try:
                session.query(self.model).filter(self.model.id == id).update(
                    {column: value}
                )
                session.commit()
                return self.read_by_id(id, eager=True)
            except SQLAlchemyError as e:
                raise e

    def whole_update(self, id: int, schema: T):
        with self.session_factory() as session:
            try:
                session.query(self.model).filter(self.model.id == id).update(
                    schema.model_dump(exclude_none=True)
                )
                session.commit()
                return self.read_by_id(id)
            except SQLAlchemyError as e:
                raise e

    def delete_by_id(self, id: int):
        with self.session_factory() as session:
            query = session.query(self.model).filter(self.model.id == id).first()
            if not query:
                raise NotFoundError(detail=f"Requested record with id: {id} does not exist.")
            try:
                session.delete(query)
                session.commit()
            except SQLAlchemyError as e:
                raise e
            except NotFoundError as e:
                raise e

    def get_unique_values(self, schema: FindUniqueValues) -> dict:
        with self.session_factory() as session:
            try:
                schema_as_dict: dict = schema.dict(exclude_none=True)

                field_name = schema_as_dict.get("field_name")
                ordering: str = schema_as_dict.get("ordering", DEFAULT_ORDERING)
                page = schema_as_dict.get("page", DEFAULT_PAGE)
                page_size = schema_as_dict.get("page_size", DEFAULT_PAGE_SIZE)
                search_term = schema_as_dict.get("search")

                column = getattr(self.model, field_name)
                if not column:
                    raise NotFoundError(detail=f"Field '{field_name}' does not exist on model {self.model.__name__}")
                query = session.query(distinct(column))

                # Handle search
                if search_term:
                    filter_condition = column.ilike(f"%{search_term}%")
                    query = query.filter(filter_condition)

                # Apply sorting
                if ordering == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())

                # Count total
                count_query = session.query(func.count(distinct(column)))
                if search_term:
                    count_query = count_query.filter(filter_condition)

                total_count = count_query.scalar()

                # Apply pagination
                if page_size != "all":
                    query = query.offset((page - 1) * page_size).limit(page_size)
                values = session.scalars(query).all()

                return {
                    "founds": values,
                    "search_options": {
                        "page": page,
                        "page_size": page_size,
                        "ordering": ordering,
                        "total_count": total_count,
                    },
                }
            except SQLAlchemyError as e:
                raise e
            except NotFoundError as e:
                raise e

    def close_scoped_session(self):
        # close the session
        with self.session_factory() as session:
            return session.close()
