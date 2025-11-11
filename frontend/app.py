import streamlit as st
import os
import requests
import pandas as pd
from urllib.parse import urljoin
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Olist Chat", layout="wide")
st.title("🛒 Olist Chat — E-commerce Assistant")

with st.sidebar:
    st.markdown("")  # small top gap
    st.markdown("### 📘 About Dataset")
    st.info("""
    Welcome! This is a Brazilian e-commerce public dataset of orders made at Olist Store.  
    It includes 100k orders (2016–2018) from multiple marketplaces in Brazil.  
    Covers order status, price, payment, freight, customer location, product attributes, and reviews.  
    Also includes a geolocation dataset mapping zip codes to lat/long.
    This is real commercial data, it has been anonymised, and references to the companies and partners 
    in the review text have been replaced with the names of Game of Thrones great houses.
    """)
    st.markdown("")  # bottom gap


# --- Initialize Session State ---
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

if "history" not in st.session_state:
    st.session_state.history = []

# --- Suggested Questions ---
SUGGESTIONS = [
    "How many customers are there?",
    "Average order value per customer",
    "Count of customers per zip code prefix",
    "Total revenue per month",
    "List products with more than 10 orders"
]

# --- Backend Chat Function ---
def call_chat(question: str):
    payload = {"session_id": st.session_state.session_id, "question": question}
    r = requests.post(urljoin(BACKEND_URL, "/chat"), json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

# --- Tabs ---
tabs = st.tabs(["💬 Chat", "📊 Query Details", "📝 Conversation History"])

# ==================================================
# CHAT TAB
# ==================================================
with tabs[0]:
    col1, col2 = st.columns([1, 3])  # Left: suggestions | Right: chat area

    # Left column: Suggested questions
    with col1:
        st.markdown("### Try these questions")
        for q in SUGGESTIONS:
            if st.button(q, key=f"sugg_{q}"):
                st.session_state.query_from_sugg = q

    # Right column: Chat interaction
    with col2:
        query = st.chat_input("Ask about the dataset or say 'hello'")

        # ---- Optional About Dataset section ----


        # Use suggestion click
        if hasattr(st.session_state, "query_from_sugg"):
            query = st.session_state.query_from_sugg
            del st.session_state.query_from_sugg

        if query:
            st.session_state.history.append({"role": "user", "text": query})
            with st.spinner("Processing..."):
                try:
                    res = call_chat(query)
                except Exception as e:
                    st.error(f"Error calling backend: {e}")
                    res = {"type": "error", "answer_text": str(e)}

            # Handle response types
            if res.get("type") == "chitchat":
                st.info(res.get("answer_text"))
                st.session_state.history.append(
                    {"role": "assistant", "text": res.get("answer_text")}
                )

            elif res.get("type") == "sql":
                st.success("✅ SQL Executed Successfully")

                st.write("**Explanation (in simple terms):**")
                st.write(res.get("explanation", ""))

                st.write("**SQL Query:**")
                st.code(res.get("sql", ""))

                df = pd.DataFrame(res.get("sample", []))
                if not df.empty:
                    st.write("**Sample Output:**")
                    st.dataframe(df, use_container_width=True)

                st.write(f"Rows returned (full): {res.get('row_count')}")
                if res.get("cache_hit", False):
                    st.success("✅ This result was served from cache")
                else:
                    st.info("⚠️ This result was freshly generated")

                st.session_state.history.append(
                    {"role": "assistant", "text": "SQL executed; see results."}
                )

# ==================================================
# QUERY DETAILS TAB
# ==================================================
with tabs[1]:
    st.subheader("📊 Last Query Details")
    if "res" in locals() and res:
        with st.expander("Cache & SQL Info"):
            cache_status = res.get("cache_hit")
            if cache_status is not None:
                st.success("✅ Cache Hit" if cache_status else "⚠️ Cache Miss")
            else:
                st.info("Cache info not available for this query.")

            if "sql" in res:
                st.write("**SQL Query:**")
                st.code(res.get("sql", ""))

            if "sample" in res:
                st.write("**Sample Output:**")
                st.dataframe(
                    pd.DataFrame(res.get("sample", [])), use_container_width=True
                )

# ==================================================
# CONVERSATION HISTORY TAB
# ==================================================
with tabs[2]:
    st.subheader("📝 Conversation History")
    for m in st.session_state.history[::-1]:
        if m["role"] == "user":
            st.markdown(f"**You:** {m['text']}")
        else:
            st.markdown(f"**Assistant:** {m['text']}")
