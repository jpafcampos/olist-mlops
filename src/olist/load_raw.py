from pathlib import Path
import duckdb

DATA_DIR = Path("data")
DB_PATH = "olist.duckdb"

# Mapeia cada CSV para o nome da tabela raw_* correspondente.
TABLES = {
    "raw_orders": "olist_orders_dataset.csv",
    "raw_order_items": "olist_order_items_dataset.csv",
    "raw_order_payments": "olist_order_payments_dataset.csv",
    "raw_order_reviews": "olist_order_reviews_dataset.csv",
    "raw_products": "olist_products_dataset.csv",
    "raw_customers": "olist_customers_dataset.csv",
    "raw_sellers": "olist_sellers_dataset.csv",
    "raw_geolocation": "olist_geolocation_dataset.csv",
    "raw_category_translation": "product_category_name_translation.csv",
}

con = duckdb.connect(DB_PATH)
for table, csv in TABLES.items():
    path = DATA_DIR / csv
    con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv_auto('{path}')")
    n = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    print(f"{table:28s} {n:>7,} lines")
con.close()