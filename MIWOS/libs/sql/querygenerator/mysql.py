from MIWOS.libs.sql.querycolumn.column import Column


class MySQLQueryGenerator:
    def __init__(self, table_name):
        self.table_name = table_name
        self.reset_query()

    @property
    def query(self):
        return f"{self.base_query} {self.where_clause} {self.limit_clause} {self.returning}"

    def create(self, columns: list):
        columns_str = ", ".join(str(column) for column in columns)
        self.base_query = f"CREATE TABLE {self.table_name} ({columns_str})"

    def is_exists(self):
        self.base_query = f"SELECT 1 FROM information_schema.tables"
        self.where_clause = f"WHERE table_name = '{self.table_name}' AND table_schema = DATABASE()"

    def drop(self):
        self.base_query = f"DROP TABLE {self.table_name}"

    def insert(self, **kwargs):
        columns = ", ".join(kwargs.keys())
        values = ", ".join(f"'{value}'" for value in kwargs.values())
        self.base_query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({values})" if kwargs else ""
        self.returning = f"RETURNING *" if kwargs else ""

    def select(self, *args):
        columns = ", ".join(args) if args else "*"
        self.base_query = f"SELECT {columns} FROM {self.table_name}"

    def delete(self):
        self.base_query = f"DELETE FROM {self.table_name}"

    def where(self, **kwargs):
        where_clause = " AND ".join(
            f"{key}='{value}'" for key, value in kwargs.items())
        self.where_clause = f"WHERE {where_clause}" if where_clause else ""

    def limit(self, limit):
        self.limit_clause = f"LIMIT {limit}"

    def reset_query(self):
        self.base_query = ""
        self.where_clause = ""
        self.limit_clause = ""
        self.returning = ""
