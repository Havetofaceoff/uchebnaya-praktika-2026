
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

        if not icon_path.is_file():
            print("Иконка не найдена:", icon_path)
            return

        try:
            self.icon_image = tk.PhotoImage(file=str(icon_path))
            self.root.iconphoto(True, self.icon_image)
        except (tk.TclError, OSError) as error:
            print("Не удалось загрузить иконку:", error)

    def create_widgets(self):
        header = tk.Frame(
            self.root,
            bg="#ffffff",
            padx=20,
            pady=15
        )
        header.pack(fill="x")

        logo_path = RESOURCES_DIR / "logo.png"

        if logo_path.is_file():
            try:
                self.logo_image = tk.PhotoImage(
                    file=str(logo_path)
                )

                tk.Label(
                    header,
                    image=self.logo_image,
                    bg="#ffffff"
                ).pack(side="left", padx=(0, 20))

            except (tk.TclError, OSError) as error:
                print("Не удалось загрузить логотип:", error)

        tk.Label(
            header,
            text="CRM: Список партнеров",
            font=("Arial", 22, "bold"),
            fg="#222222",
            bg="#ffffff"
        ).pack(side="left")

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

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

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(side="right", fill="y")
        self.table.pack(
            side="left",
            fill="both",
            expand=True
        )

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
            self.on_double_click
        )

    def on_double_click(self, event):
        # Не открываем карточку при двойном щелчке
        # по заголовку или пустой области таблицы.
        if self.table.identify_region(
            event.x, event.y
        ) == "cell":
            row = self.table.identify_row(event.y)

            if row:
                self.table.selection_set(row)
                self.edit_partner()

    def show_database_error(self, error):
        messagebox.showerror(
            "Ошибка базы данных",
            "Не удалось загрузить данные CRM.\n\n"
            "Что делать:\n"
            "1. Проверьте наличие файла clean_data.sqlite3.\n"
            "2. Убедитесь, что файл доступен.\n"
            "3. Закройте программы, которые могут "
            "блокировать базу данных.\n"
            "4. Повторно нажмите «Обновить список».\n\n"
            f"Техническая информация: {error}",
            parent=self.root
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
                "Партнёр не выбран",
                "Сначала выберите партнёра.\n\n"
                "1. Нажмите на нужную строку в таблице.\n"
                "2. Повторно нажмите кнопку "
                "«Редактировать» или «История продаж».",
                parent=self.root
            )
            return None

        values = self.table.item(
            selected[0],
            "values"
        )

        if len(values) < 2:
            messagebox.showerror(
                "Ошибка выбора",
                "Не удалось определить партнёра.\n\n"
                "1. Нажмите «Обновить список».\n"
                "2. Повторно выберите партнёра.",
                parent=self.root
            )
            return None

        try:
            partner_id = int(values[0])

            if partner_id <= 0:
                raise ValueError

        except (ValueError, TypeError):
            messagebox.showerror(
                "Некорректный ID",
                "Идентификатор партнёра некорректен.\n\n"
                "1. Обновите список партнёров.\n"
                "2. Выберите нужную строку повторно.",
                parent=self.root
            )
            return None

        return partner_id, values[1]

    def edit_partner(self):
        partner = self.get_selected_partner()

        if partner is None:
            return

        partner_id, _ = partner

        PartnerEditWindow(
            self.root,
            on_save=self.load_partners,
            partner_id=partner_id
        )

    def show_history(self):
        partner = self.get_selected_partner()

        if partner is None:
            return

        partner_id, partner_name = partner

        PartnerHistoryWindow(
            self.root,
            partner_id=partner_id,
            partner_name=partner_name
        )

    def load_partners(self):
        # Проверяем базу до очистки таблицы:
        # при ошибке уже загруженные данные останутся.
        if not DATABASE_PATH.is_file():
            self.show_database_error(
                "Файл clean_data.sqlite3 не найден"
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

        except (sqlite3.Error, OSError) as error:
            self.show_database_error(error)
            return

        for item in self.table.get_children():
            self.table.delete(item)

        for partner in partners:
            self.table.insert(
                "",
                "end",
                values=(
                    partner[0],
                    partner[1],
                    partner[2] or "Не указан",
                    partner[3],
                    partner[4] or ""
                )
            )

        print("Загружено партнеров:", len(partners))


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
