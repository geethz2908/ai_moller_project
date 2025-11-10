# backend/ingest.py
import duckdb
from pathlib import Path

DATA_DIR = Path('../data')  # put your CSVs in a folder named data/ at repo root
DB_PATH = '../olist.duckdb'  # output DB at repo root

TABLES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "product_category_translation": "product_category_name_translation.csv"
}


def ingest():
    con = duckdb.connect(DB_PATH)
    for table, fname in TABLES.items():
        fpath = DATA_DIR / fname
        if not fpath.exists():
            print(f"[WARN] Missing {fpath} — make sure you downloaded the Kaggle dataset and placed CSVs in {DATA_DIR}")
            continue
        print(f"[INFO] Loading {table} from {fpath}")
        # read_csv_auto infers column types
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv_auto('{fpath}')")
    # create a convenient joined view for analytic queries
    print("[INFO] Creating view orders_full")
    con.execute("""
    CREATE OR REPLACE VIEW orders_full AS
    SELECT o.order_id, o.customer_id, o.order_purchase_timestamp, o.order_approved_at, o.order_status,
           oi.order_item_id, oi.product_id, oi.seller_id, oi.price, oi.freight_value, oi.shipping_limit_date,
           p.product_category_name, p.product_name_lenght as product_name_length, p.product_description_lenght as product_description_length,
           c.customer_unique_id, c.customer_zip_code_prefix
    FROM orders o
    JOIN order_items oi USING(order_id)
    LEFT JOIN products p USING(product_id)
    LEFT JOIN customers c USING(customer_id)
    """)
    print("[DONE] Ingestion finished. DuckDB file:", DB_PATH)

if __name__ == "__main__":
    ingest()
