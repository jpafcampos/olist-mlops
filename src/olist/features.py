"""Fonte única da verdade das features do modelo de atraso.

Tanto o treino (train.py) quanto o serving (api.py) importam daqui,
para que a lista e a ordem das features nunca possam divergir entre
os dois lados; a base da consistência treino-serving.
"""

# A lista canônica: nome e ORDEM das features. Mudou aqui, mudou nos dois lados.
FEATURES = [
    "promised_days",
    "purchase_month",
    "purchase_dow",
    "purchase_hour",
]

# SQL que materializa alvo + features a partir de raw_orders.
STG_ORDERS_SQL = """
CREATE OR REPLACE TABLE stg_orders AS
SELECT
    order_id,
    customer_id,
    order_purchase_timestamp,
    CASE
        WHEN order_delivered_customer_date > order_estimated_delivery_date
        THEN 1 ELSE 0
    END AS late,
    month(order_purchase_timestamp)      AS purchase_month,
    dayofweek(order_purchase_timestamp)  AS purchase_dow,
    hour(order_purchase_timestamp)       AS purchase_hour,
    date_diff('day', order_purchase_timestamp,
                     order_estimated_delivery_date) AS promised_days
FROM raw_orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
"""