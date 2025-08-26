from MIWOS.libs.sql.querygenerator.mariadb import MariaDBQueryGenerator


class SQLiteQueryGenerator(MariaDBQueryGenerator):
    _anti_sql_injection_char = "?"

    def is_exists(self):
        self.base_query = f"SELECT name FROM sqlite_master"
        self.where_clause = f"WHERE type='table' AND name='{self.table_name}'"
