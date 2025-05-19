from MIWOS.libs.exceptions.locked_model_exception import LockedModelException
from MIWOS.libs.word_formatter import pluralize, singularize
from MIWOS.libs.sql.select import database_select


class Model:
    _primary_key = "id"
    _belongs_to = []
    _has_many = []

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
        for data in _query.execute(many=True):
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
        for data in _query.execute(many=True):
            model = cls()
            model._attributes = data
            model._need_creation = False
            models.append(model)
        return models

    @classmethod
    def create(cls, _many=None, **kwargs):
        if isinstance(_many, list):
            return cls.create_many(_many)
        model = cls(**kwargs)
        model.save()
        return model

    @classmethod
    def create_many(cls, many):
        _query = (database_select())(cls().table_name)
        processed_many = []
        for item in many:
            processed_item = item.copy()
            for key, value in list(processed_item.items()):
                if isinstance(value, Model):
                    processed_item[key + "_" +
                                   value._primary_key] = value._attributes[value._primary_key]
                    del processed_item[key]
            processed_many.append(processed_item)

        _query.insert_many(processed_many)
        result = _query.commit()
        models = []
        for data in result:
            model = cls()
            model._attributes = data
            model._need_creation = False
            models.append(model)
        return models

    @property
    def table_name(self):
        if not hasattr(self, "_table_name"):
            self._table_name = pluralize(self.__class__.__name__.lower())
        return self._table_name

    def save(self):
        if self._locked:
            raise LockedModelException(
                self.table_name + " is _locked. Cannot save.")
        for key, value in list(self._modified_attributes.items()):
            if isinstance(value, Model):
                self._modified_attributes[key + "_" +
                                          value._primary_key] = value._attributes[value._primary_key]
                del self._modified_attributes[key]
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

    def __str__(self):
        return self.__class__.__name__ + "(" + str(self._attributes) + ")"

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
            if name in self._belongs_to:
                return self.__parse_belongs_to(name)
            if name in self._has_many:
                return self.__parse_has_many(name)
            return None

    def __setattr__(self, obj, val):
        if obj.startswith("_"):
            super().__setattr__(obj, val)
            return
        self._modified_attributes[obj] = val

    def __parse_relation(self, name, relation_list, default_class_name_func, default_foreign_key_func, single=True):
        relation = next((x for x in relation_list if x.name == name), None)

        class_name = relation.class_name or default_class_name_func(name)
        subclasses = {cls.__name__.lower(
        ): cls for cls in Model.__subclasses__()}
        famous_model = subclasses.get(class_name.lower())
        if not famous_model:
            return None

        foreign_key = relation.foreign_key or default_foreign_key_func(
            famous_model)
        if single:
            id = self._attributes.get(foreign_key)
            if id is None:
                return None
            return famous_model.find(id)
        else:
            return famous_model.where(**{foreign_key: self._attributes[self._primary_key]})

    def __parse_belongs_to(self, name):
        return self.__parse_relation(
            name,
            self._belongs_to,
            lambda n: n,
            lambda famous_model: f"{famous_model.__name__.lower()}_{famous_model._primary_key}",
            single=True
        )

    def __parse_has_many(self, name):
        return self.__parse_relation(
            name,
            self._has_many,
            lambda n: singularize(n),
            lambda _: f"{self.__class__.__name__.lower()}_{self._primary_key}",
            single=False
        )
