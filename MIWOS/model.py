from typing import Iterable
from MIWOS.libs.exceptions.locked_model_exception import LockedModelException
from MIWOS.libs.exceptions.not_found_exception import NotFoundException
from MIWOS.libs.exceptions.validation_exception import ValidationException
from MIWOS.libs.word_formatter import pluralize, singularize
from MIWOS.libs.sql.select import database_select
from MIWOS.relation import Collection, ManyToManyRelationCollection, RelationCollection


class Model:
    _model_classes = {}
    _primary_key = "id"
    _belongs_to = []
    _has_many = []
    _has_and_belongs_to_many = []
    _hidden_attributes = []
    _validators = {}
    _default_attributes = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Model._model_classes[cls.__name__.lower()] = cls

    def __init__(self, **kwargs):
        self._query = (database_select())(self.table_name)
        self._modified_attributes = kwargs
        for key, value in self._default_attributes.items():
            if key not in self._modified_attributes:
                self._modified_attributes[key] = value
        self._attributes = {}
        self._locked = False
        self._need_creation = True
        self._relations = {}

    @classmethod
    def _from_row(cls, data):
        model = cls()
        model._attributes = data
        model._modified_attributes = {}
        model._need_creation = False
        return model

    @classmethod
    def _belongs_to_info(cls, name):
        relation = next(
            (item for item in cls._belongs_to if item.name == name), None)
        if relation is None:
            raise ValueError(
                f"Unknown belongs_to relation '{name}' on {cls.__name__}")
        related_model = Model._model_classes.get(
            (relation.class_name or name).lower())
        if related_model is None:
            raise ValueError(
                f"Model class '{relation.class_name or name}' is not loaded")
        foreign_key = relation.foreign_key or f"{name}_{related_model._primary_key}"
        return related_model, foreign_key

    @staticmethod
    def get_collection_type():
        return Collection

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
        model._modified_attributes = {}
        model._need_creation = False
        return model

    @classmethod
    def findOrFail(cls, id):
        model = cls.find(id)
        if not model:
            raise NotFoundException(f"{cls.__name__} with id {id} not found")
        return model

    @classmethod
    def replaceModelToForeignKey(cls, **kwargs):
        for key, value in list(kwargs.items()):
            if key in cls._belongs_to:
                famous_model, foreign_key = cls._belongs_to_info(key)

                if not isinstance(value, Model):
                    kwargs[foreign_key] = None
                else:
                    kwargs[foreign_key] = getattr(
                        value, famous_model._primary_key)
                del kwargs[key]
        return kwargs

    @classmethod
    def where(cls, **kwargs):
        kwargs = cls.replaceModelToForeignKey(**kwargs)

        _query = (database_select())(cls().table_name)
        _query.select("*")

        _query.where(**kwargs)
        return (cls.get_collection_type())(_query, cls)

    @classmethod
    def whereNull(cls, *args):
        _query = (database_select())(cls().table_name)
        _query.select("*")
        _query.where_null(*args)
        return (cls.get_collection_type())(_query, cls)

    @classmethod
    def whereIn(cls, **kwargs):
        return cls.all().whereIn(**kwargs)

    @classmethod
    def withRelations(cls, *names):
        return cls.all().withRelations(*names)

    @classmethod
    def whereNotNull(cls, *args):
        _query = (database_select())(cls().table_name)
        _query.select("*")
        _query.where_not_null(*args)
        return (cls.get_collection_type())(_query, cls)

    @classmethod
    def whereNot(cls, **kwargs):
        kwargs = cls.replaceModelToForeignKey(**kwargs)

        _query = (database_select())(cls().table_name)
        _query.select("*")
        _query.where_not(**kwargs)
        return (cls.get_collection_type())(_query, cls)

    @classmethod
    def orderBy(cls, *args):
        _query = (database_select())(cls().table_name)
        _query.select("*")
        _query.order_by(*args)
        return (cls.get_collection_type())(_query, cls)

    @classmethod
    def whereFirst(cls, **kwargs):
        kwargs = cls.replaceModelToForeignKey(**kwargs)

        model = cls()
        _query = (database_select())(model.table_name)
        _query.select("*")
        _query.where(**kwargs)
        _query.limit(1)
        result = _query.execute()
        if not result:
            return None
        model._attributes = result
        model._modified_attributes = {}
        model._need_creation = False
        return model

    @classmethod
    def all(cls):
        _query = (database_select())(cls().table_name)
        _query.select("*")
        return (cls.get_collection_type())(_query, cls)

    @classmethod
    def createOrFail(cls, _many=None, **kwargs):
        if isinstance(_many, list):
            models = []
            for item in cls.createMany(_many):
                models.append(item)
            return models
        model = cls(**kwargs)
        model.saveOrFail()
        return model

    @classmethod
    def create(cls, _many=None, **kwargs):
        try:
            return cls.createOrFail(_many, **kwargs)
        except ValidationException:
            return None
        except LockedModelException:
            return None

    @classmethod
    def createManyOrFail(cls, many):
        for item in many:
            model = cls(**item)
            model.saveOrFail()
            yield model

    @classmethod
    def createMany(cls, many):
        try:
            return list(cls.createManyOrFail(many))
        except ValidationException:
            return []
        except LockedModelException:
            return []

    @property
    def table_name(self):
        if not hasattr(self, "_table_name"):
            self._table_name = pluralize(self.__class__.__name__.lower())
        return self._table_name

    def validate(self):
        self.beforeValidation()
        for field, validator in self._validators.items():
            value = self._modified_attributes.get(
                field, self._attributes.get(field))
            if not validator(value):
                self.afterValidationFailure()
                self.afterValidation()
                return False
        self.afterValidationSuccess()
        self.afterValidation()
        return True

    def validateOrFail(self):
        if not self.validate():
            raise ValidationException(
                f"Validation failed for {self.__class__.__name__}")

    def saveOrFail(self):
        if self._locked:
            raise LockedModelException(
                self.table_name + " is _locked. Cannot save.")
        self.validateOrFail()
        self._modified_attributes = self.replaceModelToForeignKey(
            **self._modified_attributes)
        self.beforeSave()
        if self._need_creation:
            self._query.insert(**self._modified_attributes)
            self._attributes = self._query.commit()
        else:
            if self._modified_attributes:
                self._query.update(**self._modified_attributes)
                self._query.where(
                    **{self._primary_key: self._attributes[self._primary_key]})
                self._query.commit()
                self._attributes.update(self._modified_attributes)
        for name in tuple(self._relations):
            _, foreign_key = self._belongs_to_info(name)
            if foreign_key in self._modified_attributes:
                self._relations.pop(name)
        self._modified_attributes = {}
        self._need_creation = False
        self.afterSave()

    def save(self):
        try:
            self.saveOrFail()
        except ValidationException:
            return False
        except LockedModelException:
            return False

        return True

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

    def beforeValidation(self):
        """
        This method is called before validating the model.
        You can override this method in your model class to perform any actions before validation.
        """
        pass

    def afterValidation(self):
        """
        This method is called after validating the model.
        You can override this method in your model class to perform any actions after validation.
        """
        pass

    def afterValidationSuccess(self):
        """
        This method is called after a successful validation.
        You can override this method in your model class to perform any actions after successful validation.
        """
        pass

    def afterValidationFailure(self):
        """
        This method is called after a failed validation.
        You can override this method in your model class to perform any actions after failed validation.
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
        relations = self.__dict__.get("_relations", {})
        for relation in self._belongs_to:
            related_model = Model._model_classes.get(
                (relation.class_name or relation.name).lower())
            primary_key = related_model._primary_key if related_model else "id"
            foreign_key = relation.foreign_key or f"{relation.name}_{primary_key}"
            if obj in (relation.name, foreign_key):
                relations.pop(relation.name, None)
                if obj == foreign_key:
                    self._modified_attributes.pop(relation.name, None)
                else:
                    self._modified_attributes.pop(foreign_key, None)
        self._modified_attributes[obj] = val

    def __parse_relation(self, name, relation_list, default_class_name_func, default_foreign_key_func, single=True):
        relation = next((x for x in relation_list if x.name == name), None)

        class_name = relation.class_name or default_class_name_func(name)
        famous_model = Model._model_classes.get(class_name.lower())
        if not famous_model:
            return None

        if single:
            famous_model, foreign_key = self._belongs_to_info(name)
            if name in self._relations:
                return self._relations[name]
            id = self._modified_attributes.get(
                foreign_key, self._attributes.get(foreign_key))
            if id is None:
                return None
            return famous_model.find(id)
        else:
            foreign_key = relation.foreign_key or default_foreign_key_func(
                self.__class__)
            query = (database_select())(famous_model().table_name)
            query.select("*")
            query.where(**{foreign_key: getattr(self, self._primary_key)})
            return RelationCollection(query, famous_model)

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
            lambda famous_model: f"{famous_model.__name__.lower()}_{famous_model._primary_key}",
            single=False
        )

    def __parse_has_and_belongs_to_many(self, name):
        relation = next(
            (x for x in self._has_and_belongs_to_many if x.name == name), None)
        if not relation:
            return None

        class_name = relation.class_name or singularize(name)
        famous_model = Model._model_classes.get(class_name.lower())
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

        return ManyToManyRelationCollection(query,
                                            join_table,
                                            famous_model,
                                            foreign_key,
                                            self._attributes[self._primary_key],
                                            current_foreign_key)

    def __eq__(self, value):
        if not isinstance(value, Model):
            return False
        if self.__class__ != value.__class__:
            return False
        return self._attributes.get(self._primary_key) == value._attributes.get(value._primary_key)
