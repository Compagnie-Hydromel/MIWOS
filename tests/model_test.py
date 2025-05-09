import unittest
from MIWOS.libs.exceptions.locked_model_exception import LockedModelException
import helper


class TestModel(unittest.TestCase):
    def setUp(self):
        helper.init()
        self.model = helper.Car()

    def tearDown(self):
        helper.destroy()

    def test_initialization(self):
        self.assertIsNotNone(self.model)

    def test_get_table_name(self):
        self.assertEqual(self.model.table_name, "cars")

    def test_save(self):
        new_model = helper.Car(name="Test Car777", year=2027)
        self.assertEqual(new_model.id, None)
        self.assertEqual(new_model.name, "Test Car777")
        self.assertEqual(new_model.year, 2027)
        new_model.save()
        self.assertEqual(new_model.id, 4)
        self.assertEqual(new_model.name, "Test Car777")
        self.assertEqual(new_model.year, 2027)

    def test_delete(self):
        new_model = helper.Car(name="Test Car", year=2023)
        new_model.save()
        new_model.delete()
        self.assertRaises(LockedModelException, lambda: new_model.save())
        deleted_model = helper.Car.find(new_model.id)
        self.assertIsNone(deleted_model)

    def test_find(self):
        model = helper.Car.find(1)
        self.assertIsNotNone(model)
        self.assertEqual(model.id, 1)
        self.assertEqual(model.name, "Test Car")
        self.assertIsInstance(model, helper.Car)
        self.assertEqual(model.year, 2023)

    def test_where(self):
        models = helper.Car.where(name="Test Car")
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0].id, 1)
        self.assertEqual(models[0].name, "Test Car")
        self.assertIsInstance(models[0], helper.Car)
        self.assertEqual(models[0].year, 2023)
        self.assertEqual(models[1].id, 2)
        self.assertEqual(models[1].name, "Test Car")
        self.assertEqual(models[1].year, 2023)

    def test_all(self):
        models = helper.Car.all()
        self.assertEqual(len(models), 3)
        self.assertEqual(models[0].id, 1)
        self.assertEqual(models[0].name, "Test Car")
        self.assertIsInstance(models[0], helper.Car)
        self.assertEqual(models[0].year, 2023)
        self.assertEqual(models[1].id, 2)
        self.assertEqual(models[1].name, "Test Car")
        self.assertEqual(models[1].year, 2023)
        self.assertEqual(models[2].id, 3)
        self.assertEqual(models[2].name, "Test Car666")
        self.assertEqual(models[2].year, 2024)
