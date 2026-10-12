
import tkinter as tk
from pathlib import Path

resources = Path(__file__).resolve().parent / "resources"
resources.mkdir(exist_ok=True)

root = tk.Tk()
root.withdraw()

# Логотип компании
logo = tk.PhotoImage(width=180, height=60)
logo.put("#2563eb", to=(0, 0, 180, 60))
logo.put("#ffffff", to=(12, 12, 48, 48))
logo.put("#2563eb", to=(20, 20, 40, 40))
logo.write(str(resources / "logo.png"), format="png")

# Иконка приложения
icon = tk.PhotoImage(width=64, height=64)
icon.put("#2563eb", to=(0, 0, 64, 64))
icon.put("#ffffff", to=(12, 12, 52, 52))
icon.put("#2563eb", to=(20, 20, 44, 44))
icon.write(str(resources / "icon.png"), format="png")

root.destroy()

print("Логотип и иконка созданы!")
