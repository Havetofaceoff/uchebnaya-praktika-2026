import sqlite3
from pathlib import Path

def calculate_partner_discount(total_quantity):
    if total_quantity < 0:
        return -1

    if total_quantity < 10000:
        return 0

    if total_quantity < 50000:
        return 5

    if total_quantity < 300000:
        return 10

    return 15



def get_partner_discount(partner_id):
    database_path = (
        Path(__file__).resolve().parent.parent
        / "Инфраструктура данных и ETL (База данных в 3NF)"
        / "clean_data.sqlite3"
    )

    if not database_path.is_file():
        return -1

    try:
        with sqlite3.connect(database_path) as connection:
            partner = connection.execute(
                "SELECT partner_id FROM partners WHERE partner_id = ?",
                (partner_id,)
            ).fetchone()

            if partner is None:
                return -1

            result = connection.execute(
                """
                SELECT COALESCE(SUM(quantity), 0)
                FROM sales_history
                WHERE partner_id = ?
                """,
                (partner_id,)
            ).fetchone()

            return calculate_partner_discount(result[0])

    except sqlite3.Error:
        return -1


print(calculate_partner_discount(9999))
print(calculate_partner_discount(10000))
print(calculate_partner_discount(50000))
print(calculate_partner_discount(300000))
print("Скидка партнера 1:", get_partner_discount(1))
print("Скидка партнера 2:", get_partner_discount(2))
print("Несуществующий партнер:", get_partner_discount(999))
