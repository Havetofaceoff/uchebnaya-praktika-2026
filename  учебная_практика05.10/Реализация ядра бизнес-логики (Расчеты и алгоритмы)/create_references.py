
import sqlite3
from pathlib import Path


database_path = (
    Path(__file__).resolve().parent.parent
    / "Инфраструктура данных и ETL (База данных в 3NF)"
    / "clean_data.sqlite3"
)

with sqlite3.connect(database_path) as connection:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS product_types (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            coefficient REAL NOT NULL CHECK (coefficient >= 0)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS material_types (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            defect_percent REAL NOT NULL
                CHECK (defect_percent BETWEEN 0 AND 100)
        )
        """
    )

    connection.executemany(
        """
        INSERT OR IGNORE INTO product_types
        (id, name, coefficient)
        VALUES (?, ?, ?)
        """,
        [
            (1, "Тип продукции 1", 1.2),
            (2, "Тип продукции 2", 1.5),
            (3, "Тип продукции 3", 2.0)
        ]
    )

    connection.executemany(
        """
        INSERT OR IGNORE INTO material_types
        (id, name, defect_percent)
        VALUES (?, ?, ?)
        """,
        [
            (1, "Материал 1", 0.5),
            (2, "Материал 2", 1.0),
            (3, "Материал 3", 2.5)
        ]
    )

print("Справочники успешно созданы!")
