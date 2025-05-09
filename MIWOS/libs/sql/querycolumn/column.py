from MIWOS.libs.sql.querycolumn.enum.data_type import DataType


class Column:
    def __init__(self, name: str, data_type: DataType, **kwargs):
        self.name = name
        self.data_type = data_type
        self.null = kwargs.get('null', True)
        self.default = kwargs.get('default', None)
        self.primary_key = kwargs.get('primary_key', False)
        self.unique = kwargs.get('unique', False)
        self.auto_increment = kwargs.get('auto_increment', False)
