import mysql.connector


class MySQLQueryExecutor:
    __instance = None
    __db: mysql.connector.MySQLConnection

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(MySQLQueryExecutor, cls).__new__(cls)
        return cls.__instance

    def __init__(self, host: str, port: str, user: str, password: str, database: str, collation: str) -> None:
        if not hasattr(self, "_initialized"):
            self.__db = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                collation=collation,
            )
            self._initialized = True

    def execute(self, query: str, parameters: list = []) -> list:
        cursor = self.__db.cursor(dictionary=True)
        cursor.execute(query, parameters)
        result = cursor.fetchall()
        cursor.close()
        if len(result) == 1:
            return result[0]
        elif len(result) == 0:
            return None
        return result

    def commit(self, query: str, parameters: list = []) -> None:
        result = self.execute(query, parameters)
        self.__db.commit()
        return result
