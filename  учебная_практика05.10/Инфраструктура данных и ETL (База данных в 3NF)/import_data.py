import csv
import re
import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'clean_data.sqlite3'


def read_csv(filename, encoding='utf-8-sig'):
    with (ROOT / filename).open(encoding=encoding, newline='') as file:
        return list(csv.DictReader(file))


def clean_text(value):
    return re.sub(r'\s+', ' ', value.strip())


def normalize_date(value):
    value = value.strip()
    for fmt in ('%d.%m.%Y', '%Y/%m/%d', '%Y-%m-%d', '%d-%m-%Y', '%Y.%m.%d'):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError(f'Неизвестный формат даты: {value!r}')


def main():
    if DB.exists():
        DB.unlink()  # Внимание: повторный запуск пересоздаёт учебную базу.
    with sqlite3.connect(DB) as conn:
        conn.execute('PRAGMA foreign_keys = ON')
        conn.executescript((ROOT / 'schema.sql').read_text(encoding='utf-8'))
        for p in read_csv('partners_raw.csv'):
            conn.execute('INSERT INTO partners VALUES (?, ?, ?, ?)', (
                int(p['partner_id']), clean_text(p['partner_name']),
                p['inn'].strip(), p['email'].strip().lower()))
        for p in read_csv('products_raw.csv', 'cp1251'):
            conn.execute('INSERT INTO products VALUES (?, ?, ?)', (
                int(p['product_id']), clean_text(p['product_name']),
                str(Decimal(p['price'].strip()))))
        rejected = []
        for s in read_csv('sales_history_raw.csv'):
            partner_id, product_id = int(s['partner_id']), int(s['product_id'])
            if not conn.execute('SELECT 1 FROM partners WHERE partner_id=?', (partner_id,)).fetchone():
                rejected.append((s['sale_id'], f'Несуществующий partner_id={partner_id}'))
                continue
            if not conn.execute('SELECT 1 FROM products WHERE product_id=?', (product_id,)).fetchone():
                rejected.append((s['sale_id'], f'Несуществующий product_id={product_id}'))
                continue
            conn.execute('INSERT INTO sales_history VALUES (?, ?, ?, ?, ?, ?)', (
                int(s['sale_id']), partner_id, product_id,
                normalize_date(s['sale_date']), int(s['quantity']),
                str(Decimal(s['amount'].strip()))))
        conn.commit()
        for table in ('partners', 'products', 'sales_history'):
            print(f'{table}: {conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]} записей')
        print('Отклонённые строки:', rejected)
        print('Проверка FK:', conn.execute('PRAGMA foreign_key_check').fetchall())


if __name__ == '__main__':
    main()
