from MIWOS.libs.exceptions.locked_model_exception import LockedModelException
from MIWOS.libs.word_formatter import pluralize
from MIWOS.libs.sql.select import database_select


class Model:
    def __init__(self, **kwargs):
        self.query = (database_select())(self.table_name)
        self.modified_attributes = kwargs
        self.attributes = {}
        self.locked = False

    @classmethod
    def find(cls, id):
        model = cls()
        model.query.select("*")
        model.query.where(id=id)
        model.query.limit(1)
        result = model.query.execute()
        if not result:
            return None
        model.attributes = result
        return model

    @classmethod
    def where(cls, **kwargs):
        models = []
        query = (database_select())(cls().table_name)
        query.select("*")
        query.where(**kwargs)
        for data in query.execute():
            model = cls()
            model.attributes = data
            models.append(model)
        return models

    @classmethod
    def all(cls):
        models = []
        query = (database_select())(cls().table_name)
        query.select("*")
        for data in query.execute():
            model = cls()
            model.attributes = data
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
        if self.locked:
            raise LockedModelException("Model is locked. Cannot save.")
        self.query.insert(**self.modified_attributes)
        self.attributes = self.query.commit()
        self.modified_attributes = {}

    def delete(self):
        self.query.delete()
        self.query.where(id=self.attributes["id"])
        self.query.commit()
        self.locked = True

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name.startswith("_"):
                raise
            if name in super().__getattribute__("modified_attributes"):
                return super().__getattribute__("modified_attributes")[name]
            if name in super().__getattribute__("attributes"):
                return super().__getattribute__("attributes")[name]
