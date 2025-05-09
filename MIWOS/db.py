from MIWOS.libs.sql.select import executor_select
from MIWOS.libs.sql.migration import MigrationTable, migration_iteration, create_migrations_table_if_not_exist


def execute(query, parameters: list = []):
    return executor_select().execute(query, parameters)


def commit(query, parameters: list = []):
    return executor_select().commit(query, parameters)


def migrate():
    create_migrations_table_if_not_exist()
    for migration_instance, migration_id in migration_iteration():
        migration = MigrationTable.find(migration_id)
        if migration is not None:
            continue
        migration_instance.migrate()
        MigrationTable.create(id=migration_id)


def rollback(depth=0):
    create_migrations_table_if_not_exist()
    iteration = 0
    for migration_instance, migration_id in migration_iteration(True):
        migration = MigrationTable.find(migration_id)
        if migration is None:
            continue
        migration_instance.rollback()
        migration.delete()
        iteration += 1
        if depth > 0 and iteration >= depth:
            break
