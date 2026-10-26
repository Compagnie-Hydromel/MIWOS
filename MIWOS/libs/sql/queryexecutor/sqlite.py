import sqlite3
from threading import local
from typing import Any, List, Optional, Union

from MIWOS.config import DBConfig


class SQLiteQueryExecutor:
    __state = local()
    __db: sqlite3.Connection

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls.__state, "instance"):
            cls.__state.instance = super(SQLiteQueryExecutor, cls).__new__(cls)
        return cls.__state.instance

    def __init__(self, db_path: str) -> None:
        if getattr(self, "_initialized", False) and self._db_path != db_path:
            self.close()
        if not hasattr(self, "_initialized"):
            self.__db = sqlite3.connect(db_path)
            self.__db.row_factory = sqlite3.Row
            self._db_path = db_path
            self._initialized = True
            self.__db.execute("PRAGMA foreign_keys = ON;")

    def close(self):
        if hasattr(self, "_initialized"):
            self.__db.close()
            del self._initialized

    def execute(
        self, query: str, parameters: Union[List[Any], tuple] = [], many: bool = False
    ) -> Optional[Union[dict, List[dict]]]:
        if DBConfig.get("sql_log_file") != "":
            with open(DBConfig.get("sql_log_file"), "a") as log_file:
                log_file.write(
                    f"Executing query: {query} with parameters: {parameters}\n")

        cursor = self.__db.cursor()
        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()
        finally:
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
        try:
            result = self.execute(query, parameters, many)
            self.__db.commit()
            return result
        except Exception:
            self.__db.rollback()
            raise
