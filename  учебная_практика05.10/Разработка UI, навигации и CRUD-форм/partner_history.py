
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

        tk.Button(
            self.window,
            text="Назад",
            command=self.window.destroy,
            width=20
        ).pack(pady=15)

        self.load_history(partner_id)

    def load_history(self, partner_id):
        for item in self.table.get_children():
            self.table.delete(item)

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
                    (partner_id,)
                ).fetchall()

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
                    text="У этого партнера пока нет продаж"
                )

            print("Загружено продаж:", len(sales))

        except sqlite3.Error as error:
            messagebox.showerror(
                "Ошибка базы данных",
                str(error),
                parent=self.window
            )


