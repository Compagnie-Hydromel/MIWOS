class Association:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self):
        return self._name

    def __eq__(self, other):
        return other == self.name


class BelongsTo(Association):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self._foreign_key = kwargs.get(
            "foreign_key", None)
        self._class_name = kwargs.get("class_name", None)

    @property
    def foreign_key(self):
        return self._foreign_key

    @property
    def class_name(self):
        return self._class_name


class HasMany(BelongsTo):
    pass


class HasAndBelongsToMany(BelongsTo):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self._join_table = kwargs.get("join_table", None)
        self._current_foreign_key = kwargs.get(
            "current_foreign_key", None)
        self._verb = kwargs.get("verb", "has_and_belongs_to_many")

    @property
    def join_table(self):
        return self._join_table

    @property
    def current_foreign_key(self):
        return self._current_foreign_key

    @property
    def verb(self):
        return self._verb
