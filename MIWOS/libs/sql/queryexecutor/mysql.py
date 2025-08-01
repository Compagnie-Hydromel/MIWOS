import mysql.connector
from typing import Any, List, Optional, Union


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

    def execute(
        self, query: str, parameters: Union[List[Any], tuple] = [], many: bool = False
    ) -> Optional[Union[dict, List[dict]]]:
        cursor = self.__db.cursor()
        cursor = self.__db.cursor(dictionary=True)
        cursor.execute(query, parameters)
        result = cursor.fetchall()
        cursor.close()
        if len(result) == 1 and not many:
            return result[0]
        elif len(result) == 0:
            if many:
                return []
            return None
        return result

    def commit(
        self, query: str, parameters: Union[List[Any], tuple] = [], many: bool = False
    ) -> Optional[Union[dict, List[dict]]]:
        result = self.execute(query, parameters, many)
        self.__db.commit()
        return result
