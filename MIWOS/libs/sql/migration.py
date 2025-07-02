from MIWOS.config import DBConfig
import os
import re
from MIWOS.libs.sql.select import database_select
import MIWOS.libs.word_formatter as formatter
from MIWOS.migration import Migration
from MIWOS.model import Model


migrations_table_name = "migrations"


class MigrationsTable(Migration):
    def migrate(self):
        with self.create_tables(migrations_table_name) as x:
            x.int("id", primary_key=True)

    def rollback(self):
        self.drop_tables(migrations_table_name)


class MigrationTable(Model):
    _table_name = migrations_table_name


def migration_iteration(reverse=False):
    for filename in sorted(os.listdir(DBConfig.get("db_migration_dir")), reverse=reverse):
        regex = re.compile(r"^([0-9]{1,})_([a-z0-9_]{1,})\.py$")

        if not regex.match(filename):
            continue

        import_string = DBConfig.get("db_migration_dir").replace(
            "/", ".") + "." + filename[:-3]
        migration_module = __import__(import_string, fromlist=[""])

        classname = formatter.snake_case_to_upper_camel_case(
            regex.match(filename).group(2))

        migration_id = regex.match(filename).group(1)

        migration_class = getattr(migration_module, classname)
        migration_instance = migration_class()

        yield migration_instance, migration_id


def create_migrations_table_if_not_exist():
    query = (database_select())(migrations_table_name)
    query.is_exists()
    if query.execute() is None:
        MigrationsTable().migrate()
