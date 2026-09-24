import duckdb
from olist.features import STG_ORDERS_SQL

DB_PATH = "olist.duckdb"

con = duckdb.connect(DB_PATH)
con.execute(STG_ORDERS_SQL)

n = con.execute("SELECT count(*) FROM stg_orders").fetchone()[0]
print(f"stg_orders: {n:,} linhas")
con.close()