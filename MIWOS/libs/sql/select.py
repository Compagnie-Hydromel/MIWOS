from MIWOS.libs.exceptions.unsupported_database_connector_exception import UnsupportedDatabaseConnectorException
from MIWOS.config import DBConfig


def database_select() -> type:
    match(DBConfig.get("db_connector")):
        case "mysql":
            from MIWOS.libs.sql.mysql import MysqlQuery as Query
        case "sqlite":
            from MIWOS.libs.sql.sqlite import SqliteQuery as Query
        case _:
            raise UnsupportedDatabaseConnectorException()

    return Query


def executor_select():
    match(DBConfig.get("db_connector")):
        case "mysql":
            from MIWOS.libs.sql.queryexecutor.mysql import MySQLQueryExecutor
            db_host = DBConfig.get("db_host")
            db_port = DBConfig.get("db_port")
            db_user = DBConfig.get("db_user")
            db_password = DBConfig.get("db_password")
            db_database = DBConfig.get("db_database")
            db_collation = DBConfig.get("db_collation")
            return MySQLQueryExecutor(
                db_host, db_port, db_user, db_password, db_database, db_collation)
        case "sqlite":
            from MIWOS.libs.sql.queryexecutor.sqlite import SQLiteQueryExecutor
            db_file = DBConfig.get("db_database")
            return SQLiteQueryExecutor(db_file)
        case _:
            raise UnsupportedDatabaseConnectorException()


def columns_select() -> type:
    match(DBConfig.get("db_connector")):
        case "mysql":
            from MIWOS.libs.sql.querycolumn.mysql import MySQLColumn
            return MySQLColumn
        case "sqlite":
            from MIWOS.libs.sql.querycolumn.sqlite import SQLiteColumn
            return SQLiteColumn
        case _:
            raise UnsupportedDatabaseConnectorException()
