from typing import Iterable
from MIWOS.libs.sql.select import database_select
from typing import SupportsIndex


class RelationCollection(list):
    pass


class ManyToManyRelationCollection(RelationCollection):
    def __init__(self, iterable: Iterable, table_name: str, related_model: type,
                 related_model_foreign_key: str, model_id: int, model_foreign_key: str):
        super().__init__(iterable)
        self._query = (database_select())(table_name)
        self.related_model = related_model
        self.related_model_foreign_key = related_model_foreign_key
        self.model_foreign_key = model_foreign_key
        self.model_id = model_id

    def append(self, object, /) -> None:
        if isinstance(object, self.related_model):
            super().append(object)
            self._query.insert(**{
                self.related_model_foreign_key: object.id,
                self.model_foreign_key: self.model_id
            })
            self._query.commit()
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
        self._query.delete()
        self._query.where(
            **{self.related_model_foreign_key: item.id, self.model_foreign_key: self.model_id}
        )
        self._query.commit()
        return item

    def remove(self, value, /) -> None:
        super().remove(value)
        self._query.delete()
        self._query.where(
            **{self.related_model_foreign_key: value.id, self.model_foreign_key: self.model_id}
        )
        self._query.commit()
