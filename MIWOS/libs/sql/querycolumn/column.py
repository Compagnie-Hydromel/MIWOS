from MIWOS.libs.sql.querycolumn.enum.data_type import DataType
from MIWOS.libs.word_formatter import pluralize


class Column:
    def __init__(self, name: str, data_type: DataType, **kwargs):
        self.name = name
        self.data_type = data_type
        self.null = kwargs.get('null', True)
        self.default = kwargs.get('default', None)
        self.primary_key = kwargs.get('primary_key', False)
        self.unique = kwargs.get('unique', False)
        self.auto_increment = kwargs.get('auto_increment', False)
        self.foreign_key_table = kwargs.get(
            'foreign_key_table', pluralize(self.name))
        self.foreign_key_column = kwargs.get('foreign_key_column', "id")
        self.foreign_key = kwargs.get(
            'foreign_key', self.name + "_" + self.foreign_key_column)
        self.on_delete = kwargs.get('on_delete', None)
        self.on_update = kwargs.get('on_update', None)
        self.unique_attributes = kwargs.get('unique_attributes', [])
