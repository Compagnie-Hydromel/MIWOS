class MySQLQueryGenerator:
    def __init__(self, table_name):
        self.table_name = table_name
        self.reset_query()

    @property
    def query(self):
        return f"{self.base_query} {self.where_clause} {self.limit_clause} {self.returning}"

    def create(self, columns: list):
        columns_str = ""

        for column in columns:
            columns_str += f" {str(column)},"
            constraint = column.constraint(self.table_name)
            if constraint:
                columns_str += f"CONSTRAINT {constraint},"

        columns_str = columns_str[:-1]

        self.base_query = f"CREATE TABLE {self.table_name} ({columns_str})"

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
        values = ", ".join(self.__type_to_sqltype(value)
                           for value in kwargs.values())
        self.base_query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({values})" if kwargs else ""
        self.returning = f"RETURNING *" if kwargs else ""

    def update(self, **kwargs):
        set_clause = ", ".join(
            f"{key}={self.__type_to_sqltype(value)}" for key, value in kwargs.items())
        self.base_query = f"UPDATE {self.table_name} SET {set_clause}" if kwargs else ""

    def select(self, *args):
        columns = ", ".join(args) if args else "*"
        self.base_query = f"SELECT {columns} FROM {self.table_name}"

    def delete(self):
        self.base_query = f"DELETE FROM {self.table_name}"

    def where(self, **kwargs):
        where_clause = " AND ".join(
            f"{key}={self.__type_to_sqltype(value)}" for key, value in kwargs.items())
        self.where_clause = f"WHERE {where_clause}" if where_clause else ""

    def limit(self, limit):
        self.limit_clause = f"LIMIT {limit}"

    def reset_query(self):
        self.base_query = ""
        self.where_clause = ""
        self.limit_clause = ""
        self.returning = ""

    def __type_to_sqltype(self, value):
        if isinstance(value, bool):
            return "'1'" if value else "'0'"
        return f"'{value}'"
