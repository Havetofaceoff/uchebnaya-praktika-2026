
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pathlib import Path

from partner_edit import PartnerEditWindow
from partner_history import PartnerHistoryWindow


BASE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = BASE_DIR / "resources"

DATABASE_PATH = (
    BASE_DIR.parent
    / "Инфраструктура данных и ETL (База данных в 3NF)"
    / "clean_data.sqlite3"
)


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("CRM: Список партнеров")
        self.root.geometry("1100x650")
        self.root.configure(bg="#f5f5f5")

        self.logo_image = None
        self.icon_image = None

        self.set_app_icon()
        self.create_widgets()
        self.load_partners()

    def set_app_icon(self):
        icon_path = RESOURCES_DIR / "icon.png"

        if icon_path.is_file():
            self.icon_image = tk.PhotoImage(file=str(icon_path))
            self.root.iconphoto(True, self.icon_image)
        else:
            print("Иконка не найдена:", icon_path)

    def create_widgets(self):
        # Шапка приложения
        header = tk.Frame(
            self.root,
            bg="#ffffff",
            padx=20,
            pady=15
        )
        header.pack(fill="x")

        logo_path = RESOURCES_DIR / "logo.png"

        if logo_path.is_file():
            self.logo_image = tk.PhotoImage(file=str(logo_path))

            tk.Label(
                header,
                image=self.logo_image,
                bg="#ffffff"
            ).pack(side="left", padx=(0, 20))
        else:
            print("Логотип не найден:", logo_path)

        tk.Label(
            header,
            text="CRM: Список партнеров",
            font=("Arial", 22, "bold"),
            fg="#222222",
            bg="#ffffff"
        ).pack(side="left")

        # Оформление таблицы
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            fieldbackground="white",
            rowheight=35,
            font=("Arial", 12)
        )

        style.configure(
            "Treeview.Heading",
            background="#dddddd",
            foreground="black",
            font=("Arial", 12, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", "#cce5ff")],
            foreground=[("selected", "black")]
        )

        table_frame = tk.Frame(
            self.root,
            bg="#f5f5f5"
        )
        table_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        columns = (
            "id",
            "name",
            "type",
            "rating",
            "email"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "id": "ID",
            "name": "Наименование",
            "type": "Тип",
            "rating": "Рейтинг",
            "email": "Email"
        }

        for column, heading in headings.items():
            self.table.heading(column, text=heading)

        self.table.column("id", width=60, anchor="center")
        self.table.column("name", width=280)
        self.table.column("type", width=120, anchor="center")
        self.table.column("rating", width=100, anchor="center")
        self.table.column("email", width=250)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.table.pack(
            side="left",
            fill="both",
            expand=True
        )

        # Кнопки
        buttons = tk.Frame(
            self.root,
            bg="#f5f5f5"
        )
        buttons.pack(pady=20)

        tk.Button(
            buttons,
            text="Добавить партнера",
            command=self.add_partner,
            width=20
        ).pack(side="left", padx=8)

        tk.Button(
            buttons,
            text="Редактировать",
            command=self.edit_partner,
            width=20
        ).pack(side="left", padx=8)

        tk.Button(
            buttons,
            text="История продаж",
            command=self.show_history,
            width=20
        ).pack(side="left", padx=8)

        tk.Button(
            buttons,
            text="Обновить список",
            command=self.load_partners,
            width=20
        ).pack(side="left", padx=8)

        self.table.bind(
            "<Double-1>",
            lambda event: self.edit_partner()
        )

    def add_partner(self):
        PartnerEditWindow(
            self.root,
            on_save=self.load_partners
        )

    def get_selected_partner(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Внимание",
                "Сначала выберите партнера в таблице"
            )
            return None

        return self.table.item(selected[0], "values")

    def edit_partner(self):
        values = self.get_selected_partner()

        if values is None:
            return

        PartnerEditWindow(
            self.root,
            on_save=self.load_partners,
            partner_id=int(values[0])
        )

    def show_history(self):
        values = self.get_selected_partner()

        if values is None:
            return

        PartnerHistoryWindow(
            self.root,
            partner_id=int(values[0]),
            partner_name=values[1]
        )

    def load_partners(self):
        for item in self.table.get_children():
            self.table.delete(item)

        if not DATABASE_PATH.is_file():
            messagebox.showerror(
                "Ошибка",
                "База данных не найдена"
            )
            return

        try:
            with sqlite3.connect(DATABASE_PATH) as connection:
                partners = connection.execute(
                    """
                    SELECT
                        partner_id,
                        partner_name,
                        partner_type,
                        rating,
                        email
                    FROM partners
                    ORDER BY partner_id
                    """
                ).fetchall()

            for partner in partners:
                self.table.insert(
                    "",
                    "end",
                    values=(
                        partner[0],
                        partner[1],
                        partner[2] or "Не указан",
                        partner[3],
                        partner[4]
                    )
                )

            print("Загружено партнеров:", len(partners))

        except sqlite3.Error as error:
            messagebox.showerror(
                "Ошибка базы данных",
                str(error)
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
