# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
load_dotenv()

from .cache import cache_get, cache_set, append_session_message, get_session
from .llm_sqlgen import generate_sql_and_explanation
from .sql_executor import run_sql

app = FastAPI(title="Olist Chat Backend")

# brief schema text used as hint for SQL generation
SCHEMA_TEXT = """
orders(order_id, customer_id, order_purchase_timestamp, order_approved_at, order_status)
order_items(order_id, order_item_id, product_id, seller_id, price, freight_value)
products(product_id, product_category_name, product_name_lenght, product_description_lenght)
customers(customer_id, customer_unique_id, customer_zip_code_prefix)
orders_full(view combining orders, order_items, products, customers; contains price and product_category_name)
"""

class ChatReq(BaseModel):
    session_id: str
    question: str

class SQLReq(BaseModel):
    sql: str

@app.post("/chat")
def chat(req: ChatReq):
    cache_hit = False  # default

    # check cache
    cached = cache_get(req.question)
    if cached:
        cache_hit = True
        # store chat history
        append_session_message(req.session_id, "user", req.question)
        append_session_message(req.session_id, "assistant", "[cached] " + cached.get("answer_text",""))
        cached["cache_hit"] = cache_hit  # <-- add this
        return cached

    q = req.question.strip()
    lower = q.lower()

    # handle chit-chat locally
    if any(x in lower for x in ["hello", "hi", "hey", "how are you", "good morning", "good afternoon"]):
        answer = ("Hello! I'm your Olist e-commerce assistant. Ask me questions about sales, revenue, orders, products, sellers and reviews. "
                  "I can produce SQL, run it on the dataset, explain the SQL, and show a visualization if applicable.")
        resp = {"type": "chitchat", "answer_text": answer}
        cache_set(req.question, resp)
        append_session_message(req.session_id, "user", q)
        append_session_message(req.session_id, "assistant", answer)
        resp["cache_hit"] = False  # chit-chat just generated
        return resp

    if any(x in lower for x in ["what do you do", "overview", "what can you do", "who are you"]):
        answer = ("I am an e-commerce assistant built on the Olist dataset. I accept natural-language analytics questions, "
                  "generate safe SQL to compute aggregates on the dataset, show the results, and provide a simple human-friendly explanation of the SQL.")
        resp = {"type": "chitchat", "answer_text": answer}
        cache_set(req.question, resp)
        append_session_message(req.session_id, "user", q)
        append_session_message(req.session_id, "assistant", answer)
        resp["cache_hit"] = False
        return resp

    # For analytic questions: generate SQL, run it, return results + explanation
    try:
        sql, explanation = generate_sql_and_explanation(q, SCHEMA_TEXT)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    # run SQL
    try:
        df = run_sql(sql)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL execution error: {str(e)}")

    sample = df.head(50).to_dict(orient="records")
    result = {
        "type": "sql",
        "answer_text": "Executed SQL and returned results.",
        "sql": sql,
        "explanation": explanation,
        "row_count": len(df),
        "sample": sample,
        "columns": list(df.columns),
        "cache_hit": False  # newly generated
    }

    # store in cache
    cache_set(req.question, result)
    append_session_message(req.session_id, "user", q)
    append_session_message(req.session_id, "assistant", "Executed SQL: " + sql)
    return result


@app.post("/run_sql")
def run_sql_endpoint(payload: SQLReq):
    sql = payload.sql.strip()
    try:
        df = run_sql(sql)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"sql": sql, "row_count": len(df), "sample": df.head(200).to_dict(orient="records"), "columns": list(df.columns)}

@app.get("/session/{session_id}")
def get_session_endpoint(session_id: str):
    return get_session(session_id)
