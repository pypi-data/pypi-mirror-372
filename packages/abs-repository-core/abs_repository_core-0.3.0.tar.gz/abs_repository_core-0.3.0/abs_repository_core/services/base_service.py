from typing import Any, List, Optional, Protocol

from ..schemas import FindUniqueValues


class RepositoryProtocol(Protocol):
    def read_by_options(
        self, schema: Any
    ) -> Any: ...

    def read_by_id(self, id: int) -> Any: ...

    def create(self, schema: Any) -> Any: ...

    def bulk_create(self, schemas: List[Any]) -> Any: ...

    def update(self, id: int, schema: Any) -> Any: ...

    def update_attr(self, id: int, attr: str, value: Any) -> Any: ...

    def whole_update(self, id: int, schema: Any) -> Any: ...

    def delete_by_id(self, id: int) -> Any: ...

    def get_unique_values(self, schema: Any) -> Any: ...

    def read_by_attr(self, attr: str, value: Any, eager: bool) -> Any: ...
class BaseService:
    def __init__(self, repository: RepositoryProtocol) -> None:
        self._repository = repository

    def get_list(
        self, schema: Any = None
    ) -> Any:
        return self._repository.read_by_options(schema, eager=True)

    def get_by_id(self, id: int) -> Any:
        return self._repository.read_by_id(id, eager=True)

    def add(self, schema: Any) -> Any:
        return self._repository.create(schema)
    
    def bulk_add(self, schemas: List[Any]) -> Any:
        return self._repository.bulk_create(schemas)

    def patch(self, id: int, schema: Any) -> Any:
        return self._repository.update(id, schema)

    def patch_attr(self, id: int, attr: str, value: Any) -> Any:
        return self._repository.update_attr(id, attr, value)

    def put_update(self, id: int, schema: Any) -> Any:
        return self._repository.whole_update(id, schema)

    def remove_by_id(self, id: int) -> Any:
        return self._repository.delete_by_id(id)

    def get_unique_values(self, schema: FindUniqueValues) -> dict:
        return self._repository.get_unique_values(schema)
    
    def get_by_attr(self, attr: str, value: Any, eager: bool = False) -> Any:
        return self._repository.read_by_attr(attr, value, eager)
