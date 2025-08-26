class DBConfig:
    _config = {
        "db_connector": "mariadb",
        "db_host": "localhost",
        "db_port": 3306,
        "db_user": "",
        "db_password": "",
        "db_database": "",
        "db_collation": "utf8mb4_general_ci",
        "db_migration_dir": "migrations",
        "sql_log_file": ""
    }

    @classmethod
    def set(cls, **kwargs):
        cls._config.update(kwargs)

    @classmethod
    def get(cls, key):
        return cls._config.get(key)

    @classmethod
    def all(cls):
        return dict(cls._config)
