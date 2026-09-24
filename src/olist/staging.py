import duckdb

DB_PATH = "olist.duckdb"

STG_ORDERS_SQL = """
CREATE OR REPLACE TABLE stg_orders AS
SELECT
    order_id,
    customer_id,
    order_purchase_timestamp,                    -- guardado p/ o split temporal (passo 5)

    -- ALVO: entregou depois do prometido?
    CASE
        WHEN order_delivered_customer_date > order_estimated_delivery_date
        THEN 1 ELSE 0
    END AS late,

    -- FEATURES disponíveis NO MOMENTO DA COMPRA (sem vazamento)
    month(order_purchase_timestamp)      AS purchase_month,   -- 1..12
    dayofweek(order_purchase_timestamp)  AS purchase_dow,     -- 0=domingo .. 6=sábado
    hour(order_purchase_timestamp)       AS purchase_hour,    -- 0..23
    date_diff('day', order_purchase_timestamp,
                     order_estimated_delivery_date) AS promised_days
FROM raw_orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
"""

con = duckdb.connect(DB_PATH)
con.execute(STG_ORDERS_SQL)

n = con.execute("SELECT count(*) FROM stg_orders").fetchone()[0]
print(f"stg_orders: {n:,} linhas")

con.sql("SELECT * FROM stg_orders LIMIT 5").show()

# sanity check das features e do alvo
con.sql("""
    SELECT
        round(100.0 * avg(late), 1)      AS pct_late,
        round(avg(promised_days), 1)     AS avg_promised,
        min(promised_days)               AS min_promised,
        max(promised_days)               AS max_promised
    FROM stg_orders
""").show()
con.close()