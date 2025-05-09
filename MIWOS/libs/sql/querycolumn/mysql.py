from MIWOS.libs.sql.querycolumn.column import Column
from MIWOS.libs.sql.querycolumn.enum.data_type import DataType
from MIWOS.libs.exceptions.unsupported_data_type_exception import UnsupportedDataTypeException


class MySQLColumn(Column):
    @property
    def __data_type_to_string(self):
        match self.data_type:
            case DataType.INT:
                return "INTEGER"
            case DataType.FLOAT:
                return "FLOAT"
            case DataType.STRING:
                return "TEXT"
            case DataType.BOOLEAN:
                return "BOOLEAN"
            case DataType.DATE:
                return "DATE"
            case DataType.DATETIME:
                return "DATETIME"
            case _:
                raise UnsupportedDataTypeException(self.data_type)

    def __str__(self):
        column_definition = f"{self.name} {self.__data_type_to_string}"
        if not self.null:
            column_definition += " NOT NULL"
        if self.default is not None:
            column_definition += f" DEFAULT {self.default}"
        if self.primary_key:
            column_definition += " PRIMARY KEY"
        if self.unique:
            column_definition += " UNIQUE"
        if self.auto_increment:
            column_definition += " AUTO_INCREMENT"
        return column_definition
