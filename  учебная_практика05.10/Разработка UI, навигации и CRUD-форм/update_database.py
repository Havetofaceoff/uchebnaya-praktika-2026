
import sqlite3
from pathlib import Path


database_path = (
    Path(__file__).resolve().parent.parent
    / "Инфраструктура данных и ETL (База данных в 3NF)"
    / "clean_data.sqlite3"
)

new_columns = {
    "partner_type": "TEXT",
    "rating": "INTEGER NOT NULL DEFAULT 0 CHECK (rating >= 0)",
    "address": "TEXT",
    "director": "TEXT",
    "phone": "TEXT"
}

if not database_path.is_file():
    raise FileNotFoundError("База данных не найдена")

with sqlite3.connect(database_path) as connection:
    existing_columns = {
        column[1]
        for column in connection.execute(
            "PRAGMA table_info(partners)"
        ).fetchall()
    }

    for column_name, column_type in new_columns.items():
        if column_name not in existing_columns:
            connection.execute(
                f"ALTER TABLE partners ADD COLUMN {column_name} {column_type}"
            )

print("База данных успешно обновлена!")
