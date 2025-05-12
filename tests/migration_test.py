import unittest

from MIWOS.libs.exceptions.unsupported_data_type_exception import UnsupportedDataTypeException
from MIWOS.migration import Migration
import helper


class TestMigrationClass(Migration):
    def migrate(self):
        self.create_tables(
            "test_table", lambda x: x.integer("id", primary_key=True))


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
                          lambda: TestMigrationClass().migrate())
