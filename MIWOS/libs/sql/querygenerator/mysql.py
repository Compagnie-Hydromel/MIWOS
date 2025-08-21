from MIWOS.libs.word_formatter import singularize


class MySQLQueryGenerator:
    _anti_sql_injection_char = "%s"

    def __init__(self, table_name):
        self.table_name = table_name
        self.reset_query()

    @property
    def query(self):
        return f"{self.base_query} {self.where_clause} {self.order_by_clause} {self.limit_clause} {self.returning}"

    @property
    def arguments(self):
        return self.arguments_insert + self.arguments_update + self.arguments_where

    def create(self, columns: list):
        columns_str = ""

        for column in columns:
            str_column = str(column)
            if str_column == "":
                continue
            columns_str += f" {str_column},"
        for column in columns:
            constraint = column.constraint(self.table_name)
            if constraint:
                columns_str += f"CONSTRAINT {constraint},"

        columns_str = columns_str[:-1]

        self.base_query = f"CREATE TABLE {self.table_name} ({columns_str})"

    def create_join_table(self, left_table, right_table, left_table_primary_key="id", right_table_primary_key="id", can_have_duplicates=False):
        left_table_s = singularize(left_table)
        right_table_s = singularize(right_table)

        primary_key = "id INT PRIMARY KEY AUTO_INCREMENT" if can_have_duplicates else f"PRIMARY KEY ({left_table_s}_{left_table_primary_key}, {right_table_s}_{right_table_primary_key})"

        self.base_query = f"CREATE TABLE {self.table_name} (" \
            f"{left_table_s}_{left_table_primary_key} INT NOT NULL, " \
            f"{right_table_s}_{right_table_primary_key} INT NOT NULL, " \
            f"{primary_key}, " \
            f"FOREIGN KEY ({left_table_s}_{left_table_primary_key}) REFERENCES {left_table}({left_table_primary_key}) ON DELETE CASCADE, " \
            f"FOREIGN KEY ({right_table_s}_{right_table_primary_key}) REFERENCES {right_table}({right_table_primary_key}) ON DELETE CASCADE" \
            f")"

    def add_columns(self, columns: list):
        columns_str = ""

        for column in columns:
            columns_str += f"ADD COLUMN {str(column)},"
            constraint = column.constraint(self.table_name)
            if constraint:
                columns_str += f"ADD CONSTRAINT {constraint},"

        columns_str = columns_str[:-1]

        self.base_query = f"ALTER TABLE {self.table_name}  {columns_str}"

    def is_exists(self):
        self.base_query = f"SELECT 1 FROM information_schema.tables"
        self.where_clause = f"WHERE table_name = '{self.table_name}' AND table_schema = DATABASE()"

    def drop(self):
        self.base_query = f"DROP TABLE {self.table_name}"

    def insert(self, **kwargs):
        columns = ", ".join(kwargs.keys())
        placeholders = ", ".join(
            self._anti_sql_injection_char for _ in kwargs.values())
        self.base_query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})" if kwargs else ""
        self.returning = f"RETURNING *" if kwargs else ""
        self.arguments_insert = list(kwargs.values())

    def update(self, **kwargs):
        set_clause = ", ".join(
            f"{key}=" + self._anti_sql_injection_char for key in kwargs.keys())
        self.base_query = f"UPDATE {self.table_name} SET {set_clause}" if kwargs else ""
        self.arguments_update = list(kwargs.values())

    def select(self, *args):
        columns = ", ".join(args) if args else "*"
        self.base_query = f"SELECT {columns} FROM {self.table_name}"

    def delete(self):
        self.base_query = f"DELETE FROM {self.table_name}"

    def where(self, **kwargs):
        where_clause = " AND ".join(
            f"{key}=" + self._anti_sql_injection_char for key in kwargs.keys())
        self.where_clause += f" AND {where_clause}" if self.where_clause else f"WHERE {where_clause}"
        self.arguments_where += list(kwargs.values())

    def where_null(self, *args):
        where_clause = " AND ".join(f"{arg} IS NULL" for arg in args)
        self.where_clause += f" AND {where_clause}" if self.where_clause else f"WHERE {where_clause}"

    def where_not_null(self, *args):
        where_clause = " AND ".join(f"{arg} IS NOT NULL" for arg in args)
        self.where_clause += f" AND {where_clause}" if self.where_clause else f"WHERE {where_clause}"

    def where_not(self, **kwargs):
        where_clause = " AND ".join(
            f"{key}<>" + self._anti_sql_injection_char for key in kwargs.keys())
        self.where_clause += f" AND {where_clause}" if self.where_clause else f"WHERE {where_clause}"
        self.arguments_where += list(kwargs.values())

    def inner_join(self, table, on_condition):
        self.base_query += f" INNER JOIN {table} ON {on_condition}"

    def limit(self, limit):
        self.limit_clause = f"LIMIT {limit}"

    def order_by(self, *args):
        order_by_clause = ", ".join(args)
        self.order_by_clause = f" ORDER BY {order_by_clause} " if order_by_clause else ""

    def reset_query(self):
        self.base_query = ""
        self.where_clause = ""
        self.order_by_clause = ""
        self.limit_clause = ""
        self.returning = ""
        self.arguments_update = []
        self.arguments_insert = []
        self.arguments_where = []
