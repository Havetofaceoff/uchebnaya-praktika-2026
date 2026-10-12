
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pathlib import Path


DATABASE_PATH = (
    Path(__file__).resolve().parent.parent
    / "Инфраструктура данных и ETL (База данных в 3NF)"
    / "clean_data.sqlite3"
)


class PlaceholderEntry(tk.Entry):
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(parent, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = "#888888"
        self.normal_color = "#222222"
        self.placeholder_visible = False

        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

        self.show_placeholder()

    def show_placeholder(self):
        if not self.get() and self.placeholder:
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)
            self.placeholder_visible = True

    def on_focus_in(self, event):
        if self.placeholder_visible:
            self.delete(0, tk.END)
            self.config(fg=self.normal_color)
            self.placeholder_visible = False

    def on_focus_out(self, event):
        if not self.get():
            self.show_placeholder()

    def get_value(self):
        if self.placeholder_visible:
            return ""
        return self.get().strip()

    def set_value(self, value):
        self.delete(0, tk.END)
        self.placeholder_visible = False
        self.config(fg=self.normal_color)

        if value is not None and str(value) != "":
            self.insert(0, str(value))
        else:
            self.show_placeholder()


class PartnerEditWindow:
    def __init__(self, parent, on_save=None, partner_id=None):
        self.on_save = on_save
        self.partner_id = partner_id
        self.original_data = None

        self.window = tk.Toplevel(parent)
        self.window.title(
            "CRM: Редактирование партнера"
            if partner_id is not None
            else "CRM: Добавление партнера"
        )
        self.window.geometry("580x730")
        self.window.minsize(500, 650)
        self.window.configure(bg="#f5f5f5")

        title_text = (
            "Редактирование партнера"
            if partner_id is not None
            else "Добавление партнера"
        )

        tk.Label(
            self.window,
            text=title_text,
            font=("Arial", 20, "bold"),
            bg="#f5f5f5",
            fg="#222222"
        ).pack(pady=20)

        form = tk.Frame(
            self.window,
            bg="#f5f5f5"
        )
        form.pack(
            fill="both",
            expand=True,
            padx=40
        )

        self.entries = {}

        fields = [
            (
                "partner_name",
                "Наименование",
                "Введите название организации"
            ),
            (
                "inn",
                "ИНН",
                "Введите ИНН организации"
            ),
            (
                "rating",
                "Рейтинг",
                "Введите целое число от 0"
            ),
            (
                "address",
                "Адрес",
                "Город, улица, дом"
            ),
            (
                "director",
                "Директор",
                "Фамилия Имя Отчество"
            ),
            (
                "phone",
                "Телефон",
                "+7 (999) 123-45-67"
            ),
            (
                "email",
                "Email",
                "example@mail.ru"
            )
        ]

        for key, label_text, placeholder in fields:
            tk.Label(
                form,
                text=label_text,
                font=("Arial", 11),
                bg="#f5f5f5",
                fg="#222222",
                anchor="w"
            ).pack(
                fill="x",
                pady=(8, 3)
            )

            entry = PlaceholderEntry(
                form,
                placeholder=placeholder,
                font=("Arial", 12),
                bg="white",
                relief="solid",
                borderwidth=1
            )
            entry.pack(
                fill="x",
                ipady=5
            )

            self.entries[key] = entry

        tk.Label(
            form,
            text="Тип организации",
            font=("Arial", 11),
            bg="#f5f5f5",
            fg="#222222"
        ).pack(
            anchor="w",
            pady=(8, 3)
        )

        self.partner_type = ttk.Combobox(
            form,
            values=["ООО", "ИП", "ЗАО", "ОАО", "ПАО"],
            state="readonly",
            font=("Arial", 12)
        )
        self.partner_type.pack(fill="x")
        self.partner_type.set("ООО")

        buttons = tk.Frame(
            self.window,
            bg="#f5f5f5"
        )
        buttons.pack(pady=20)

        tk.Button(
            buttons,
            text="Сохранить",
            command=self.save_partner,
            width=16,
            bg="#2563eb",
            fg="black",
            font=("Arial", 12)
        ).pack(
            side="left",
            padx=10
        )

        tk.Button(
            buttons,
            text="Назад",
            command=self.close_window,
            width=16,
            font=("Arial", 12)
        ).pack(
            side="left",
            padx=10
        )

        # Закрытие крестиком тоже проверяет изменения.
        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.close_window
        )

        if self.partner_id is not None:
            if not self.load_partner():
                return

        # Запоминаем состояние формы до редактирования.
        self.original_data = self.get_form_data()

    def get_form_data(self):
        data = {
            key: entry.get_value()
            for key, entry in self.entries.items()
        }

        data["partner_type"] = self.partner_type.get()
        return data

    def close_window(self):
        if (
            self.original_data is not None
            and self.get_form_data() != self.original_data
        ):
            confirm = messagebox.askyesno(
                "Несохранённые изменения",
                "Вы изменили данные партнёра, "
                "но не сохранили их.\n\n"
                "Если выйти сейчас, изменения "
                "будут потеряны.\n\n"
                "Выйти без сохранения?",
                parent=self.window
            )

            if not confirm:
                return

        self.window.destroy()

    def show_database_error(self, error):
        messagebox.showerror(
            "Ошибка базы данных",
            "Не удалось выполнить операцию "
            "с базой данных.\n\n"
            "Что делать:\n"
            "1. Проверьте наличие файла clean_data.sqlite3.\n"
            "2. Убедитесь, что файл доступен для чтения "
            "и записи.\n"
            "3. Закройте программы, которые могут "
            "блокировать базу.\n"
            "4. Повторите операцию.\n\n"
            f"Техническая информация: {error}",
            parent=self.window
        )

    def load_partner(self):
        try:
            if not DATABASE_PATH.is_file():
                raise sqlite3.OperationalError(
                    "Файл базы данных не найден"
                )

            with sqlite3.connect(DATABASE_PATH) as connection:
                partner = connection.execute(
                    """
                    SELECT
                        partner_name,
                        inn,
                        partner_type,
                        rating,
                        address,
                        director,
                        phone,
                        email
                    FROM partners
                    WHERE partner_id = ?
                    """,
                    (self.partner_id,)
                ).fetchone()

            if partner is None:
                messagebox.showerror(
                    "Партнёр не найден",
                    "Не удалось открыть карточку партнёра.\n\n"
                    "1. Вернитесь к списку партнёров.\n"
                    "2. Обновите список.\n"
                    "3. Повторно выберите партнёра.",
                    parent=self.window
                )
                self.window.destroy()
                return False

            keys = [
                "partner_name",
                "inn",
                "partner_type",
                "rating",
                "address",
                "director",
                "phone",
                "email"
            ]

            data = dict(zip(keys, partner))

            for key, entry in self.entries.items():
                entry.set_value(data.get(key))

            partner_type = data.get("partner_type")

            if partner_type in self.partner_type["values"]:
                self.partner_type.set(partner_type)
            else:
                self.partner_type.set("ООО")

            return True

        except sqlite3.Error as error:
            self.show_database_error(error)
            self.window.destroy()
            return False

    def save_partner(self):
        name = self.entries["partner_name"].get_value()
        inn = self.entries["inn"].get_value()

        if not name or not inn:
            messagebox.showwarning(
                "Ошибка заполнения",
                "Не удалось сохранить партнёра.\n\n"
                "1. Заполните поле «Наименование».\n"
                "2. Заполните поле «ИНН».\n"
                "3. Повторно нажмите «Сохранить».",
                parent=self.window
            )
            return

        rating_text = self.entries["rating"].get_value()

        try:
            rating = int(rating_text) if rating_text else 0

            if rating < 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Некорректный рейтинг",
                "Рейтинг должен быть целым "
                "неотрицательным числом.\n\n"
                "1. Введите число, например 0, 5 или 10.\n"
                "2. Не используйте отрицательные "
                "или дробные значения.\n"
                "3. Повторите сохранение.",
                parent=self.window
            )
            return

        values = (
            name,
            inn,
            self.partner_type.get(),
            rating,
            self.entries["address"].get_value(),
            self.entries["director"].get_value(),
            self.entries["phone"].get_value(),
            self.entries["email"].get_value()
        )

        try:
            if not DATABASE_PATH.is_file():
                raise sqlite3.OperationalError(
                    "Файл базы данных не найден"
                )

            with sqlite3.connect(DATABASE_PATH) as connection:
                if self.partner_id is None:
                    connection.execute(
                        """
                        INSERT INTO partners (
                            partner_name,
                            inn,
                            partner_type,
                            rating,
                            address,
                            director,
                            phone,
                            email
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        values
                    )

                else:
                    cursor = connection.execute(
                        """
                        UPDATE partners
                        SET
                            partner_name = ?,
                            inn = ?,
                            partner_type = ?,
                            rating = ?,
                            address = ?,
                            director = ?,
                            phone = ?,
                            email = ?
                        WHERE partner_id = ?
                        """,
                        values + (self.partner_id,)
                    )

                    if cursor.rowcount == 0:
                        messagebox.showerror(
                            "Партнёр не найден",
                            "Не удалось сохранить изменения.\n\n"
                            "1. Вернитесь к списку партнёров.\n"
                            "2. Обновите список.\n"
                            "3. Проверьте, существует ли "
                            "этот партнёр.",
                            parent=self.window
                        )
                        return

                connection.commit()

            # Сохранение прошло успешно.
            self.original_data = self.get_form_data()

            messagebox.showinfo(
                "Успех",
                "Данные партнёра успешно сохранены!",
                parent=self.window
            )

            if self.on_save:
                self.on_save()

            self.window.destroy()

        except sqlite3.Error as error:
            self.show_database_error(error)
