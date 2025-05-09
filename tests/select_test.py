import unittest
from MIWOS.config import init
from MIWOS.libs.sql.select import columns_select, database_select, executor_select
from MIWOS.libs.exceptions.unsupported_database_connector_exception import UnsupportedDatabaseConnectorException


class TestSelectFunctions(unittest.TestCase):
    def setUp(self):
        init(db_connector="mysql_but_not_supported")

    def test_columns_select_unsupported(self):
        self.assertRaises(UnsupportedDatabaseConnectorException,
                          lambda: columns_select())

    def test_database_select_unsupported(self):
        self.assertRaises(UnsupportedDatabaseConnectorException,
                          lambda: database_select())

    def test_executor_select_unsupported(self):
        self.assertRaises(UnsupportedDatabaseConnectorException,
                          lambda: executor_select())
