from MIWOS.libs.sql.querycolumn.column import Column
from MIWOS.libs.sql.querycolumn.enum.data_type import DataType
from MIWOS.libs.exceptions.unsupported_data_type_exception import UnsupportedDataTypeException


class MySQLColumn(Column):
    @property
    def __data_type_to_string(self):
        match self.data_type:
            case DataType.INT | DataType.PRIMARY_KEY | DataType.REFERENCES | DataType.INTEGER:
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
            case DataType.TIMESTAMP:
                return "TIMESTAMP"
            case DataType.BIGINT:
                return "BIGINT"
            case _:
                raise UnsupportedDataTypeException(self.data_type)

    def __str__(self):
        if self.data_type == DataType.REFERENCES:
            column_definition = f"{self.foreign_key} {self.__data_type_to_string}"
        elif len(self.unique_attributes) > 0:
            return ""
        else:
            column_definition = f"{self.name} {self.__data_type_to_string}"

        if not self.null:
            column_definition += " NOT NULL"
        if self.default is not None:
            column_definition += f" DEFAULT {self.default}"
        if self.primary_key or self.data_type == DataType.PRIMARY_KEY:
            column_definition += " PRIMARY KEY"
        if self.unique:
            column_definition += " UNIQUE"
        if self.auto_increment:
            column_definition += " AUTO_INCREMENT"
        if self.on_update:
            column_definition += f" ON UPDATE {self.on_update}"

        return column_definition

    def constraint(self, table_name: str = None):
        constraint = ""
        if self.data_type == DataType.REFERENCES:
            constraint += f"fk_{table_name}_{self.foreign_key} FOREIGN KEY ({self.foreign_key}) REFERENCES {self.foreign_key_table}({self.foreign_key_column})"
            if self.on_delete:
                constraint += f" ON DELETE {self.on_delete}"
        elif self.unique_attributes:
            constraint += f"uq_{table_name}_{'_'.join(self.unique_attributes)} UNIQUE ({', '.join(self.unique_attributes)})"

        return constraint
