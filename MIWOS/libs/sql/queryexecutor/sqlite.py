import sqlite3
from typing import Any, List, Optional, Union

from build.lib.MIWOS.config import DBConfig


class SQLiteQueryExecutor:
    __instance = None
    __db: sqlite3.Connection

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(SQLiteQueryExecutor, cls).__new__(cls)
        return cls.__instance

    def __init__(self, db_path: str) -> None:
        if not hasattr(self, "_initialized"):
            self.__db = sqlite3.connect(db_path)
            self.__db.row_factory = sqlite3.Row
            self._initialized = True

    def execute(
        self, query: str, parameters: Union[List[Any], tuple] = [], many: bool = False
    ) -> Optional[Union[dict, List[dict]]]:
        if DBConfig.get("sql_log_file") != "":
            with open(DBConfig.get("sql_log_file"), "a") as log_file:
                log_file.write(
                    f"Executing query: {query} with parameters: {parameters}\n")

        cursor = self.__db.cursor()
        cursor.execute(query, parameters)
        rows = cursor.fetchall()
        cursor.close()
        result = [dict(row) for row in rows]
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
