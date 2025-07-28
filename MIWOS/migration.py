from MIWOS.libs.exceptions.unsupported_data_type_exception import UnsupportedDataTypeException
from MIWOS.libs.sql.querycolumn.enum.data_type import DataType
from MIWOS.libs.sql.select import database_select, columns_select
from contextlib import contextmanager


class Migration:
    def migrate(self):
        pass

    def rollback(self):
        pass

    @contextmanager
    def create_tables(self, table_name):
        query = (database_select())(table_name)
        columns = Migration.ColumnsManager()
        yield columns
        query.create(columns.columns)
        query.commit()

    @contextmanager
    def add_columns(self, table_name):
        query = (database_select())(table_name)
        columns = Migration.ColumnsManager()
        yield columns
        query.add_columns(columns.columns)
        query.commit()

    def drop_tables(self, *table_names):
        for table_name in table_names:
            query = (database_select())(table_name)
            query.drop()
            query.commit()

    def create_join_table(self, left_table, right_table, **kwargs):
        right_table_primary_key = kwargs.get(
            "right_table_primary_key", "id")
        left_table_primary_key = kwargs.get(
            "left_table_primary_key", "id")

        verb = kwargs.get("verb", "has_and_belongs_to_many")

        can_have_duplicates = kwargs.get(
            "can_have_duplicates", False)

        sort_table_name = [left_table, right_table]
        sort_table_name.sort()

        table_name = kwargs.get(
            "table_name", f"{sort_table_name[0]}_{verb}_{sort_table_name[1]}")

        query = (database_select())(table_name)

        query.create_join_table(
            left_table, right_table,
            left_table_primary_key=left_table_primary_key,
            right_table_primary_key=right_table_primary_key,
            can_have_duplicates=can_have_duplicates
        )
        query.commit()

    def drop_join_table(self, left_table, right_table, **kwargs):
        verb = kwargs.get("verb", "has_and_belongs_to_many")
        sort_table_name = [left_table, right_table]
        sort_table_name.sort()
        table_name = kwargs.get(
            "table_name", f"{sort_table_name[0]}_{verb}_{sort_table_name[1]}")

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
