import unittest

from MIWOS.libs.exceptions.unsupported_data_type_exception import UnsupportedDataTypeException
from MIWOS.migration import Migration
import helper


class TestMigrationClassFail(Migration):
    def migrate(self):
        self.create_tables(
            "test_table", lambda x: x.integer("id", primary_key=True))


class TestMigrationSuccess(Migration):
    def migrate(self):
        self.create_tables(
            "test_table_seconds", lambda x: x.primary_key("id"))
        self.create_tables(
            "test_tables", lambda x: x.primary_key("id", primary_key=True))
        self.add_columns(
            "test_tables", lambda x: x.string("name", unique=True))
        self.add_columns(
            "test_tables", lambda x: x.references("test_table_second", on_delete="CASCADE",
                                                  on_update="CASCADE"))

    def rollback(self):
        self.drop_tables("test_tables")
        self.drop_tables("test_table_seconds")


class TestMigration(unittest.TestCase):
    def setUp(self):
        helper.init()

    def tearDown(self):
        helper.destroy()

    def test_migration(self):
        Migration().migrate()

    def test_rollback(self):
        Migration().rollback()

    def test_invalid_type_migration(self):
        self.assertRaises(UnsupportedDataTypeException,
                          lambda: TestMigrationClassFail().migrate())

    def test_success_migration(self):
        self.assertIsNone(TestMigrationSuccess().migrate())
        self.assertIsNone(TestMigrationSuccess().rollback())
