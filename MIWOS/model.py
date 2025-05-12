from MIWOS.libs.exceptions.locked_model_exception import LockedModelException
from MIWOS.libs.word_formatter import pluralize
from MIWOS.libs.sql.select import database_select


class Model:
    _primary_key = "id"

    def __init__(self, **kwargs):
        self._query = (database_select())(self.table_name)
        self._modified_attributes = kwargs
        self._attributes = {}
        self._locked = False
        self._need_creation = True

    @classmethod
    def find(cls, id):
        model = cls()
        model._query.select("*")
        model._query.where(
            **{cls._primary_key: id})
        model._query.limit(1)
        result = model._query.execute()
        if not result:
            return None
        model._attributes = result
        model._need_creation = False
        return model

    @classmethod
    def where(cls, **kwargs):
        models = []
        _query = (database_select())(cls().table_name)
        _query.select("*")
        _query.where(**kwargs)
        for data in _query.execute():
            model = cls()
            model._attributes = data
            model._need_creation = False
            models.append(model)
        return models

    @classmethod
    def all(cls):
        models = []
        _query = (database_select())(cls().table_name)
        _query.select("*")
        for data in _query.execute():
            model = cls()
            model._attributes = data
            model._need_creation = False
            models.append(model)
        return models

    @classmethod
    def create(cls, **kwargs):
        model = cls(**kwargs)
        model.save()
        return model

    @property
    def table_name(self):
        if not hasattr(self, "_table_name"):
            self._table_name = pluralize(self.__class__.__name__.lower())
        return self._table_name

    def save(self):
        if self._locked:
            raise LockedModelException(
                self.table_name + " is _locked. Cannot save.")
        if self._need_creation:
            self._query.insert(**self._modified_attributes)
            self._attributes = self._query.commit()
        else:
            self._query.update(**self._modified_attributes)
            self._query.where(
                **{self._primary_key: self._attributes[self._primary_key]})
            self._query.commit()
            self._attributes.update(self._modified_attributes)
        self._modified_attributes = {}
        self._need_creation = False

    def delete(self):
        self._query.delete()
        self._query.where(
            **{self._primary_key: self._attributes[self._primary_key]})
        self._query.commit()
        self._locked = True

    def __getattr__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name.startswith("_"):
                raise
            if name in self._modified_attributes:
                return self._modified_attributes[name]
            if name in self._attributes:
                return self._attributes[name]

    def __setattr__(self, obj, val):
        if obj.startswith("_"):
            super().__setattr__(obj, val)
            return
        self._modified_attributes[obj] = val
