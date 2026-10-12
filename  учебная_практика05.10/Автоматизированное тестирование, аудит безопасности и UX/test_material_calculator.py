
import unittest
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import sys
from pathlib import Path

CALCULATOR_DIR = (
    Path(__file__).resolve().parent.parent
    / "Реализация ядра бизнес-логики (Расчеты и алгоритмы)"
)

sys.path.insert(0, str(CALCULATOR_DIR))

import material_calculator


class TestMaterialCalculator(unittest.TestCase):

    def setUp(self):
        # Отдельная временная БД защищает учебные данные.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.sqlite3"

        with sqlite3.connect(self.db_path) as connection:
            connection.executescript(
                """
                CREATE TABLE product_types (
                    id INTEGER PRIMARY KEY,
                    coefficient REAL NOT NULL
                );

                CREATE TABLE material_types (
                    id INTEGER PRIMARY KEY,
                    defect_percent REAL NOT NULL
                );

                INSERT INTO product_types VALUES (1, 1.5);
                INSERT INTO product_types VALUES (2, 1.0);

                INSERT INTO material_types VALUES (1, 10);
                INSERT INTO material_types VALUES (2, 0);
                """
            )

        self.db_patch = patch.object(
            material_calculator,
            "DATABASE_PATH",
            self.db_path
        )
        self.db_patch.start()

    def tearDown(self):
        self.db_patch.stop()
        self.temp_dir.cleanup()

    def test_basic_calculation(self):
        result = material_calculator.calculate_material(
            1, 1, 10, 2, 3
        )
        self.assertEqual(result, 99)

    def test_rounding_up(self):
        result = material_calculator.calculate_material(
            2, 2, 1, 1.1, 1
        )
        self.assertEqual(result, 2)

    def test_invalid_product_id(self):
        result = material_calculator.calculate_material(
            999, 1, 10, 2, 3
        )
        self.assertEqual(result, -1)

    def test_invalid_material_id(self):
        result = material_calculator.calculate_material(
            1, 999, 10, 2, 3
        )
        self.assertEqual(result, -1)

    def test_negative_quantity(self):
        result = material_calculator.calculate_material(
            1, 1, -10, 2, 3
        )
        self.assertEqual(result, -1)

    def test_negative_parameter(self):
        result = material_calculator.calculate_material(
            1, 1, 10, -2, 3
        )
        self.assertEqual(result, -1)

    def test_zero_quantity(self):
        result = material_calculator.calculate_material(
            1, 1, 0, 2, 3
        )
        self.assertEqual(result, 0)

    def test_invalid_input_type(self):
        result = material_calculator.calculate_material(
            1, 1, "abc", 2, 3
        )
        self.assertEqual(result, -1)

    def test_negative_material_parameter(self):
        result = material_calculator.calculate_material(
            1, 1, 10, 2, -3
        )
        self.assertEqual(result, -1)

    def test_database_unavailable(self):
        material_calculator.DATABASE_PATH = (
            self.db_path.parent / "missing" / "database.sqlite3"
        )

        result = material_calculator.calculate_material(
            1, 1, 10, 2, 3
        )
        self.assertEqual(result, -1)


if __name__ == "__main__":
    unittest.main()
