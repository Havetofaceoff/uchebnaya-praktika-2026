
import math
import sqlite3
from pathlib import Path


DATABASE_PATH = (
    Path(__file__).resolve().parent.parent
    / "Инфраструктура данных и ETL (База данных в 3NF)"
    / "clean_data.sqlite3"
)


def calculate_material(
    product_type_id,
    material_type_id,
    quantity,
    parameter_1,
    parameter_2
):
    try:
        # Проверяем корректность числовых параметров.
        values = (quantity, parameter_1, parameter_2)

        if any(
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value < 0
            for value in values
        ):
            return -1

        if (
            type(product_type_id) is not int
            or type(material_type_id) is not int
            or product_type_id <= 0
            or material_type_id <= 0
        ):
            return -1

        with sqlite3.connect(DATABASE_PATH) as connection:
            product_type = connection.execute(
                """
                SELECT coefficient
                FROM product_types
                WHERE id = ?
                """,
                (product_type_id,)
            ).fetchone()

            material_type = connection.execute(
                """
                SELECT defect_percent
                FROM material_types
                WHERE id = ?
                """,
                (material_type_id,)
            ).fetchone()

        if product_type is None or material_type is None:
            return -1

        coefficient = float(product_type[0])
        defect_percent = float(material_type[0])

        if (
            not math.isfinite(coefficient)
            or not math.isfinite(defect_percent)
            or coefficient < 0
            or defect_percent < 0
        ):
            return -1

        material_amount = (
            quantity
            * parameter_1
            * parameter_2
            * coefficient
            * (1 + defect_percent / 100)
        )

        if not math.isfinite(material_amount):
            return -1

        # Материал закупается целыми единицами,
        # поэтому даже дробный остаток округляем вверх.
        return math.ceil(round(material_amount, 10))

    except (sqlite3.Error, TypeError, ValueError, OverflowError, OSError):
        return -1


if __name__ == "__main__":
    print("Обычный расчет:", calculate_material(1, 1, 100, 2, 3))
    print("Другой материал:", calculate_material(2, 3, 50, 4, 2))
    print("Неверный ID:", calculate_material(999, 1, 100, 2, 3))
    print("Отрицательное количество:", calculate_material(1, 1, -100, 2, 3))
