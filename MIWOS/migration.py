from MIWOS.libs.exceptions.unsupported_data_type_exception import UnsupportedDataTypeException
from MIWOS.libs.sql.querycolumn.enum.data_type import DataType
from MIWOS.libs.sql.select import database_select, columns_select


class Migration:
    def migrate(self):
        pass

    def rollback(self):
        pass

    def create_tables(self, table_name, columns_function):
        query = (database_select())(table_name)
        columns = Migration.ColumnsManager()
        columns_function(columns)

        query.create(columns.columns)
        query.commit()

    def drop_tables(self, table_name):
        query = (database_select())(table_name)
        query.drop()
        query.commit()

    class ColumnsManager:
        def __init__(self):
            self.columns = []
            self.column_type = columns_select()

        def __getattr__(self, name):
            def add_column(column_name, **kwargs):
                data_type = getattr(DataType, name.upper(), None)
                self.columns.append(self.column_type(
                    column_name, data_type, **kwargs))
            return add_column
