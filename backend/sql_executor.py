# backend/sql_executor.py
import duckdb
import pandas as pd
import os
import re

DB_PATH = os.getenv("DUCKDB_PATH", "../olist.duckdb")

def is_safe_sql(sql: str) -> bool:
    """Allow only SELECT queries roughly. This is a simple check, not a full parser."""
    s = sql.strip().lower()
    # disallow semicolons that chain multiple statements
    if ';' in s and not s.strip().endswith(';'):
        return False
    # allow only SELECT statements
    return s.startswith('select')

def run_sql(sql: str):
    sql_clean = sql.strip().rstrip(';')
    if not is_safe_sql(sql_clean):
        raise ValueError("Only single SELECT queries are allowed.")
    con = duckdb.connect(DB_PATH)
    df = con.execute(sql_clean).fetchdf()
    return df
