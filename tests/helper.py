from MIWOS.model import Model
from MIWOS.config import init as init_MIWOS
from os import getenv
from dotenv import load_dotenv

init_MIWOS(
    db_connector=getenv("DB_CONNECTOR") or "mysql",
    db_host=getenv("DB_HOST") or "localhost",
    db_port=getenv("DB_PORT") or "3306",
    db_user=getenv("DB_USER") or "",
    db_password=getenv("DB_PASSWORD") or "",
    db_database=getenv("DB_DATABASE") or "",
    db_collation=getenv("DB_COLLATION") or "utf8mb4_general_ci",
    db_migration_dir="tests/migrations",
)


class Car(Model):
    pass


def init():
    load_dotenv()

    from MIWOS import db
    db.migrate()

    Car.create(
        id=1,
        name="Test Car",
        year=2023,
    )
    Car.create(
        id=2,
        name="Test Car",
        year=2023,
    )
    Car.create(
        id=3,
        name="Test Car666",
        year=2024,
    )


def destroy():
    from MIWOS import db
    from MIWOS.libs.sql.migration import MigrationsTable

    db.rollback()
    MigrationsTable().rollback()
