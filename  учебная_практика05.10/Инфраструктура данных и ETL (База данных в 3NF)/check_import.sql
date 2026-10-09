PRAGMA foreign_keys = ON;
PRAGMA foreign_key_check;
SELECT 'partners' AS table_name, COUNT(*) AS row_count FROM partners
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'sales_history', COUNT(*) FROM sales_history;
SELECT sale_id, partner_id, product_id, sale_date, quantity, amount FROM sales_history ORDER BY sale_id;
SELECT partner_id, partner_name, inn, email FROM partners ORDER BY partner_id;
