from MIWOS.libs.exceptions.locked_model_exception import LockedModelException
from MIWOS.libs.word_formatter import pluralize, singularize
from MIWOS.libs.sql.select import database_select


class Model:
    _primary_key = "id"
    _belongs_to = []
    _has_many = []
    _has_and_belongs_to_many = []
    _hidden_attributes = []

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

    @staticmethod
    def replaceModelToForeignKey(**kwargs):
        for key, value in list(kwargs.items()):
            if isinstance(value, Model):
                kwargs[key + "_" +
                       value._primary_key] = value._attributes[value._primary_key]
                del kwargs[key]
        return kwargs

    @classmethod
    def where(cls, **kwargs):
        kwargs = cls.replaceModelToForeignKey(**kwargs)

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
    def whereFirst(cls, **kwargs):
        kwargs = cls.replaceModelToForeignKey(**kwargs)

        model = cls()
        _query = (database_select())(cls().table_name)
        _query.select("*")
        _query.where(**kwargs)
        _query.limit(1)
        result = _query.execute()
        if not result:
            return None
        model._attributes = result
        model._need_creation = False
        return model

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
            models = []
            for item in cls.createMany(_many):
                models.append(item)
            return models
        model = cls(**kwargs)
        model.save()
        return model

    @classmethod
    def createMany(cls, many):
        for item in many:
            model = cls(**item)
            model.save()
            yield model

    @property
    def table_name(self):
        if not hasattr(self, "_table_name"):
            self._table_name = pluralize(self.__class__.__name__.lower())
        return self._table_name

    def save(self):
        if self._locked:
            raise LockedModelException(
                self.table_name + " is _locked. Cannot save.")
        self._modified_attributes = self.replaceModelToForeignKey(
            **self._modified_attributes)
        self.beforeSave()
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
        self.afterSave()

    def delete(self):
        self._query.delete()
        self._query.where(
            **{self._primary_key: self._attributes[self._primary_key]})
        self._query.commit()
        self._locked = True

    def isDirty(self, name):
        if name in self._modified_attributes:
            return True
        return False

    def beforeSave(self):
        """
        This method is called before saving the model.
        You can override this method in your model class to perform any actions before saving.
        """
        pass

    def afterSave(self):
        """
        This method is called after saving the model.
        You can override this method in your model class to perform any actions after saving.
        """
        pass

    def beforeDelete(self):
        """
        This method is called before deleting the model.
        You can override this method in your model class to perform any actions before deleting.
        """
        pass

    def afterDelete(self):
        """
        This method is called after deleting the model.
        You can override this method in your model class to perform any actions after deleting.
        """
        pass

    def to_dict(self):
        """
        Convert the model instance to a dictionary representation.
        """
        return {key: value for key, value in self._attributes.items() if key not in self._hidden_attributes}

    def __str__(self):
        attribute = self._attributes

        return self.__class__.__name__ + "(" + ", ".join(
            [f"{key}={value}" for key, value in attribute.items() if key not in self._hidden_attributes]) + ")"

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
            if name in self._has_and_belongs_to_many:
                return self.__parse_has_and_belongs_to_many(name)
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

    def __parse_has_and_belongs_to_many(self, name):
        relation = next(
            (x for x in self._has_and_belongs_to_many if x.name == name), None)
        if not relation:
            return None

        class_name = relation.class_name or singularize(name)
        subclasses = {cls.__name__.lower(
        ): cls for cls in Model.__subclasses__()}
        famous_model = subclasses.get(class_name.lower())
        if not famous_model:
            return None

        current_foreign_key = relation.current_foreign_key or f"{self.__class__.__name__.lower()}_{self._primary_key}"

        foreign_key = relation.foreign_key or f"{famous_model.__name__.lower()}_{famous_model._primary_key}"

        verb = relation.verb or "has_and_belongs_to_many"

        sort_class_name = [pluralize(self.__class__.__name__.lower()), pluralize(
            class_name.lower())]

        sort_class_name.sort()

        join_table = relation.join_table or f"{sort_class_name[0]}_{verb}_{sort_class_name[1]}"

        query = (database_select())(pluralize(name))

        query.select(name + ".*")
        query.inner_join(
            join_table, f"{join_table}.{foreign_key}={name}.{famous_model._primary_key}")
        query.where(
            **{current_foreign_key: self._attributes[self._primary_key]})

        results = query.execute(many=True)
        models = []
        for data in results:
            model = famous_model()
            model._attributes = data
            model._need_creation = False
            models.append(model)

        return models
