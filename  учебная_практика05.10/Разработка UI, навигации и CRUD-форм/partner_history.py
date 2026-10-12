
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pathlib import Path


DATABASE_PATH = (
    Path(__file__).resolve().parent.parent
    / "Инфраструктура данных и ETL (База данных в 3NF)"
    / "clean_data.sqlite3"
)


class PartnerHistoryWindow:
    def __init__(self, parent, partner_id, partner_name):
        self.partner_id = partner_id

        self.window = tk.Toplevel(parent)
        self.window.title("CRM: История продаж")
        self.window.geometry("950x550")
        self.window.configure(bg="#f5f5f5")

        title = tk.Label(
            self.window,
            text=f"История продаж: {partner_name}",
            font=("Arial", 18, "bold"),
            fg="#222222",
            bg="#f5f5f5"
        )
        title.pack(pady=20)

        table_frame = tk.Frame(
            self.window,
            bg="#f5f5f5"
        )
        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        columns = (
            "product",
            "date",
            "quantity",
            "amount"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "product": "Товар",
            "date": "Дата продажи",
            "quantity": "Количество",
            "amount": "Сумма"
        }

        for column, heading in headings.items():
            self.table.heading(
                column,
                text=heading
            )

        self.table.column("product", width=320)
        self.table.column("date", width=180, anchor="center")
        self.table.column("quantity", width=140, anchor="center")
        self.table.column("amount", width=180, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(side="right", fill="y")
        self.table.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.status_label = tk.Label(
            self.window,
            text="",
            font=("Arial", 11),
            fg="#555555",
            bg="#f5f5f5"
        )
        self.status_label.pack(pady=5)

        buttons = tk.Frame(
            self.window,
            bg="#f5f5f5"
        )
        buttons.pack(pady=15)

        tk.Button(
            buttons,
            text="Обновить",
            command=self.load_history,
            width=20
        ).pack(side="left", padx=10)

        tk.Button(
            buttons,
            text="Назад",
            command=self.window.destroy,
            width=20
        ).pack(side="left", padx=10)

        self.load_history()

    def show_database_error(self, error):
        messagebox.showerror(
            "Ошибка базы данных",
            "Не удалось загрузить историю продаж.\n\n"
            "Что делать:\n"
            "1. Проверьте наличие файла clean_data.sqlite3.\n"
            "2. Убедитесь, что файл доступен для чтения.\n"
            "3. Закройте программы, которые могут "
            "блокировать базу данных.\n"
            "4. Нажмите «Обновить» для повторной попытки.\n\n"
            f"Техническая информация: {error}",
            parent=self.window
        )

    def load_history(self):
        # Проверяем ID перед передачей в SQL-запрос.
        if (
            type(self.partner_id) is not int
            or self.partner_id <= 0
        ):
            self.status_label.config(
                text="Ошибка: некорректный ID партнёра"
            )
            messagebox.showerror(
                "Некорректный ID",
                "Не удалось определить партнёра.\n\n"
                "1. Закройте историю продаж.\n"
                "2. Обновите список партнёров.\n"
                "3. Выберите партнёра повторно.",
                parent=self.window
            )
            return

        if not DATABASE_PATH.is_file():
            self.status_label.config(
                text="История продаж недоступна"
            )
            self.show_database_error(
                "Файл clean_data.sqlite3 не найден"
            )
            return

        try:
            with sqlite3.connect(DATABASE_PATH) as connection:
                sales = connection.execute(
                    """
                    SELECT
                        COALESCE(
                            p.product_name,
                            'Товар не найден'
                        ) AS product_name,
                        s.sale_date,
                        s.quantity,
                        s.amount
                    FROM sales_history AS s
                    LEFT JOIN products AS p
                        ON s.product_id = p.product_id
                    WHERE s.partner_id = ?
                    ORDER BY s.sale_date DESC
                    """,
                    (self.partner_id,)
                ).fetchall()

        except (sqlite3.Error, OSError) as error:
            self.status_label.config(
                text="Не удалось обновить историю продаж"
            )
            self.show_database_error(error)
            return

        # Обновляем таблицу только после успешного запроса.
        for item in self.table.get_children():
            self.table.delete(item)

        for sale in sales:
            self.table.insert(
                "",
                "end",
                values=(
                    sale[0],
                    sale[1],
                    sale[2],
                    sale[3]
                )
            )

        if sales:
            self.status_label.config(
                text=f"Всего продаж: {len(sales)}"
            )
        else:
            self.status_label.config(
                text="У этого партнёра пока нет продаж"
            )

        print("Загружено продаж:", len(sales))
