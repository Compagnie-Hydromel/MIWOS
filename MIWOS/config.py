db_connector = "mysql"
db_host = "localhost"
db_port = 3306
db_user = ""
db_password = ""
db_database = ""
db_collation = "utf8mb4_general_ci"
db_migration_dir = "migrations"


def init(**kwargs):
    """
    Initialize the database connection with the given parameters.
    """
    global db_connector, db_host, db_port, db_user, db_password, db_database, db_collation, db_migration_dir
    db_connector = kwargs.get("db_connector", "mysql")
    db_host = kwargs.get("db_host", "localhost")
    db_port = kwargs.get("db_port", 3306)
    db_user = kwargs.get("db_user", "")
    db_password = kwargs.get("db_password", "")
    db_database = kwargs.get("db_database", "")
    db_collation = kwargs.get("db_collation", "utf8mb4_general_ci")
    db_migration_dir = kwargs.get("db_migration_dir", "migrations")
