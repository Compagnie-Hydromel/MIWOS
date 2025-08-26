from MIWOS.config import DBConfig
from os import getenv


def init():
    DBConfig.set(
        db_connector=getenv("DB_CONNECTOR") or "mariadb",
        db_host=getenv("DB_HOST") or "localhost",
        db_port=getenv("DB_PORT") or "3306",
        db_user=getenv("DB_USER") or "",
        db_password=getenv("DB_PASSWORD") or "",
        db_database=getenv("DB_DATABASE") or "",
        db_collation=getenv("DB_COLLATION") or "utf8mb4_general_ci",
        db_migration_dir="db/migrations",
        sql_log_file="sql.log"
    )
