
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
    if quantity < 0 or parameter_1 < 0 or parameter_2 < 0:
        return -1

    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            product_type = connection.execute(
                "SELECT coefficient FROM product_types WHERE id = ?",
                (product_type_id,)
            ).fetchone()

            material_type = connection.execute(
                "SELECT defect_percent FROM material_types WHERE id = ?",
                (material_type_id,)
            ).fetchone()

            if product_type is None or material_type is None:
                return -1

            coefficient = product_type[0]
            defect_percent = material_type[0]

            if coefficient < 0 or defect_percent < 0:
                return -1

            material_amount = (
                quantity
                * parameter_1
                * parameter_2
                * coefficient
                * (1 + defect_percent / 100)
            )

            return material_amount

    except (sqlite3.Error, TypeError, ValueError):
        return -1

if __name__ == "__main__":
    print("Обычный расчет:", calculate_material(1, 1, 100, 2, 3))
    print("Другой материал:", calculate_material(2, 3, 50, 4, 2))
    print("Неверный ID:", calculate_material(999, 1, 100, 2, 3))
    print("Отрицательное количество:", calculate_material(1, 1, -100, 2, 3))
    print("Отрицательный параметр:", calculate_material(1, 1, 100, -2, 3))
