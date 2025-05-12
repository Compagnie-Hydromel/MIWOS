from MIWOS.libs.exceptions.unsupported_database_connector_exception import UnsupportedDatabaseConnectorException


def database_select() -> type:
    from MIWOS.config import db_connector

    match(db_connector):
        case "mysql":
            from MIWOS.libs.sql.mysql import MysqlQuery as Query
        case _:
            raise UnsupportedDatabaseConnectorException()

    return Query


def executor_select():
    from MIWOS.config import db_connector, db_host, db_port, db_user, db_password, db_database, db_collation

    match(db_connector):
        case "mysql":
            from MIWOS.libs.sql.queryexecutor.mysql import MySQLQueryExecutor
            return MySQLQueryExecutor(
                db_host, db_port, db_user, db_password, db_database, db_collation)
        case _:
            raise UnsupportedDatabaseConnectorException()


def columns_select() -> type:
    from MIWOS.config import db_connector

    match(db_connector):
        case "mysql":
            from MIWOS.libs.sql.querycolumn.mysql import MySQLColumn
            return MySQLColumn
        case _:
            raise UnsupportedDatabaseConnectorException()
