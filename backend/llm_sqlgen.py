# backend/llm_sqlgen.py
import os
import re
from google import genai   # google-genai SDK
from dotenv import load_dotenv
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

if not GEMINI_KEY:
    raise RuntimeError("Please set GEMINI_API_KEY in .env")

# configure client (SDK picks key from env var or you can pass in configure)
client = genai.Client(api_key=GEMINI_KEY)


def extract_first_select(text: str) -> str:
    """Extract the first SELECT ... ; block or the first SELECT... to end if no semicolon."""
    pattern = re.compile(r"(select[\s\S]*?;)", flags=re.IGNORECASE)
    m = pattern.search(text)
    if m:
        return m.group(1)
    # fallback: try to find everything from first SELECT to end
    m2 = re.search(r"(select[\s\S]*)", text, flags=re.IGNORECASE)
    if m2:
        return m2.group(1).strip()
    return text.strip()

def generate_sql_and_explanation(question: str, schema_text: str):
    """Return (sql, explanation)."""
    # Prompt: ask for SQL only (single SELECT)
    prompt_sql = f"""
You are an assistant that receives a plain-English analytics question and MUST produce exactly one valid SQL SELECT statement
that can run on DuckDB using the schema below. Output ONLY the SQL; do NOT output any explanation or extra text.

Schema:
{schema_text}

Rules:
- Output a single SELECT statement (limit to at most one statement).
- Use explicit GROUP BY when aggregating.
- Use ISO dates like '2017-01-01' if filtering by year/month.
- Use table/view names exactly as given.
Question: {question}
"""
    # Ask Gemini to generate SQL
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        # many SDKs accept 'prompt' or 'contents'; this field may vary slightly depending on the SDK version
        # Here we use 'input' via "text" like examples from docs.
        contents=prompt_sql
    )
    # response structure varies across SDK versions; try common fields
    txt = None
    # try common attributes
    if hasattr(response, 'text'):
        txt = response.text
    elif isinstance(response, dict):
        # try candidate field
        txt = response.get("candidates", [{}])[0].get("content", "")
        if not txt:
            txt = response.get("output", "")
    else:
        # fallback to str
        txt = str(response)

    # extract SQL safely
    sql_raw = extract_first_select(txt)
    # ensure it ends with semicolon
    if not sql_raw.strip().endswith(';'):
        sql_raw = sql_raw.strip() + ';'

    # Now ask for a simple explanation
    explain_prompt = f"Explain the following SQL in 2-3 simple sentences for a non-technical user:\n\n{sql_raw}"
    resp2 = client.models.generate_content(model=GEMINI_MODEL, contents=explain_prompt)
    explanation = None
    if hasattr(resp2, 'text'):
        explanation = resp2.text
    elif isinstance(resp2, dict):
        explanation = resp2.get("candidates", [{}])[0].get("content", "")
    else:
        explanation = str(resp2)

    # cleanup explanation
    explanation = explanation.strip()
    return sql_raw.strip(), explanation
