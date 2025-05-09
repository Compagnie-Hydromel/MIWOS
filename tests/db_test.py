import unittest
import helper
import MIWOS.db as db
from mysql.connector.errors import ProgrammingError


class TestModel(unittest.TestCase):
    def setUp(self):
        helper.init()

    def tearDown(self):
        helper.destroy()

    def test_execute(self):
        self.assertEqual(
            db.execute("SELECT * FROM cars WHERE id = %s", (1,)),
            {
                "id": 1,
                "name": "Test Car",
                "year": 2023,
            }
        )

    def test_commit(self):
        db.commit(
            "INSERT INTO cars (id, name, year) VALUES (%s, %s, %s)", (4, "New Car", 2024))

        self.assertEqual(
            db.execute("SELECT * FROM cars WHERE id = %s", (4,)),
            {
                "id": 4,
                "name": "New Car",
                "year": 2024,
            }
        )

    def test_rollback(self):
        db.rollback()

        self.assertRaises(
            ProgrammingError,
            lambda: db.execute("SELECT * FROM cars WHERE id = %s", (3,))
        )

    def test_rollback_depth(self, depth=1):
        db.rollback(1)

        db.execute("SELECT * FROM cars WHERE id = %s", (3,))

        self.assertRaises(
            ProgrammingError,
            lambda: db.execute("SELECT * FROM humans WHERE id = %s", (3,))
        )

    def test_migrate(self):
        db.migrate()

        self.assertEqual(
            db.execute("SELECT * FROM cars WHERE id = %s", (1,)),
            {
                "id": 1,
                "name": "Test Car",
                "year": 2023,
            }
        )
