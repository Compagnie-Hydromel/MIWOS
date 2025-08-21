from typing import Iterable
from MIWOS.libs.sql.select import database_select
from typing import SupportsIndex


class Collection(list):
    def __init__(self, query, current_model, iterable: Iterable = ()):
        super().__init__(iterable)
        self._query = query
        self._current_model = current_model
        self._fetched_data = False

    def where(self, **kwargs):
        if not self._fetched_data:
            self._query.where(**kwargs)
        return self

    def whereNull(self, *args):
        if not self._fetched_data:
            self._query.where_null(*args)
        return self

    def whereNotNull(self, *args):
        if not self._fetched_data:
            self._query.where_not_null(*args)
        return self

    def whereNot(self, **kwargs):
        if not self._fetched_data:
            self._query.where_not(**kwargs)
        return self

    def orderBy(self, *args):
        if not self._fetched_data:
            self._query.order_by(*args)
        return self

    def limit(self, limit: int):
        if not self._fetched_data:
            self._query.limit(limit)
        return self

    def _ensure_fetched(method):
        def wrapper(self, *args, **kwargs):
            if not self._fetched_data:
                self.fetch()
            return method(self, *args, **kwargs)
        return wrapper

    def fetch(self):
        if self._fetched_data:
            return
        for data in self._query.execute(many=True):
            model = self._current_model()
            model._attributes = data
            model._modified_attributes = {}
            model._need_creation = False
            super().append(model)
        self._fetched_data = True

    @_ensure_fetched
    def append(self, object, /) -> None:
        super().append(object)

    @_ensure_fetched
    def remove(self, value, /) -> None:
        super().remove(value)

    @_ensure_fetched
    def pop(self, index: SupportsIndex = -1, /):
        return super().pop(index)

    @_ensure_fetched
    def clear(self) -> None:
        super().clear()

    @_ensure_fetched
    def __len__(self) -> int:
        return super().__len__()

    @_ensure_fetched
    def __str__(self) -> str:
        return super().__str__()

    @_ensure_fetched
    def __repr__(self) -> str:
        return super().__repr__()

    @_ensure_fetched
    def __contains__(self, item) -> bool:
        return super().__contains__(item)

    @_ensure_fetched
    def __getitem__(self, index):
        return super().__getitem__(index)

    @_ensure_fetched
    def __iter__(self):
        return super().__iter__()

    @_ensure_fetched
    def extend(self, iterable):
        return super().extend(iterable)

    @_ensure_fetched
    def index(self, value, start=0, stop=None):
        return super().index(value, start, stop)

    @_ensure_fetched
    def count(self, value):
        return super().count(value)


class RelationCollection(Collection):
    pass


class ManyToManyRelationCollection(RelationCollection):
    def __init__(self, query, table_name: str, related_model: type,
                 related_model_foreign_key: str, model_id: int, model_foreign_key: str, iterable: Iterable = []):
        super().__init__(query, related_model, iterable)
        self._insert_query = (database_select())(table_name)
        self.related_model = related_model
        self.related_model_foreign_key = related_model_foreign_key
        self.model_foreign_key = model_foreign_key
        self.model_id = model_id

    def append(self, object, /) -> None:
        if isinstance(object, self.related_model):
            super().append(object)
            self._insert_query.insert(**{
                self.related_model_foreign_key: object.id,
                self.model_foreign_key: self.model_id
            })
            self._insert_query.commit()
        else:
            raise TypeError(
                f"Expected item of type {self.related_model.__name__}, got {type(object).__name__}")

    def find(self, id: int):
        for item in self:
            if item.id == id:
                return item
        return None

    def extend(self, iterable: Iterable, /) -> None:
        for item in iterable:
            self.append(item)

    def pop(self, index: SupportsIndex = -1, /):
        item = super().pop(index)
        self._insert_query.delete()
        self._insert_query.where(
            **{self.related_model_foreign_key: item.id, self.model_foreign_key: self.model_id}
        )
        self._insert_query.commit()
        return item

    def remove(self, value, /) -> None:
        super().remove(value)
        self._insert_query.delete()
        self._insert_query.where(
            **{self.related_model_foreign_key: value.id, self.model_foreign_key: self.model_id}
        )
        self._insert_query.commit()

    def clear(self) -> None:
        super().clear()
        self._insert_query.delete()
        self._insert_query.where(**{self.model_foreign_key: self.model_id})
        self._insert_query.commit()
