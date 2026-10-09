PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS partners (
    partner_id INTEGER PRIMARY KEY,
    partner_name TEXT NOT NULL CHECK (length(trim(partner_name)) > 0),
    inn TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL CHECK (length(trim(product_name)) > 0),
    price DECIMAL(12, 2) NOT NULL CHECK (price >= 0)
);

CREATE TABLE IF NOT EXISTS sales_history (
    sale_id INTEGER PRIMARY KEY,
    partner_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    sale_date TEXT NOT NULL CHECK (sale_date GLOB '????-??-??'),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    amount DECIMAL(14, 2) NOT NULL CHECK (amount >= 0),
    FOREIGN KEY (partner_id) REFERENCES partners(partner_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
