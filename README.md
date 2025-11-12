---

# 🛒 Olist Chat — Natural Language E-commerce Analytics Assistant

Olist Chat is an **AI-powered analytics assistant** built using the **Olist Brazilian E-commerce dataset** from Kaggle.  
It allows users to **ask natural-language questions** about sales, revenue, orders, and products, and automatically:

* Generates corresponding **SQL queries** using **Google Gemini**,
* Executes the SQL safely on a local or deployed **DuckDB database**,
* Explains the query in simple language,
* Returns a structured **data table** and **summary explanation**,
* Caches responses for performance optimization, and
* Stores **conversation history** for every user session.

> 🚀 **Live Demo:** [Olist Chat on Render](https://ai-moller-project.onrender.com/) — try it directly in your browser!

---

## 📦 Dataset

**Dataset Name:** [Olist Brazilian E-commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/)

This dataset contains information from an e-commerce platform (Olist) operating in Brazil, including:

* Orders placed by customers  
* Products sold by multiple sellers  
* Payment details  
* Delivery times  
* Customer reviews  
* Geolocation data  

It provides a realistic foundation for business intelligence and analytics tasks such as sales trends, order analysis, and product performance.

---

## ⚙️ Features Overview

### 1. 💬 Natural Language to SQL
* Users can type questions like *“What is the total revenue in 2017?”*
* The **Google Gemini API** automatically generates a **valid SQL query** based on the dataset schema.

  ```sql
  SELECT SUM(price) AS total_revenue 
  FROM orders_full 
  WHERE order_purchase_timestamp >= '2017-01-01' 
    AND order_purchase_timestamp < '2018-01-01';


### 2. 🧠 SQL Explanation

* Once the query is generated, the system also uses Gemini to produce a **simple explanation** of what the SQL does — written in human-friendly terms.

### 3. 🗃️ Query Execution

* The generated SQL runs against a **DuckDB database** (created from the Olist CSV files).
* **Only safe `SELECT` queries** are executed to prevent harmful operations.

### 4. ⚡ Caching System (Redis)

* The system uses **Redis** to cache query results and chat sessions.
* When a user repeats a question, the answer is instantly served from cache.

### 5. 💾 Conversation History

* All user interactions and assistant responses are stored persistently (per session).
* Makes it easy to maintain **chat context** and revisit past queries.

### 6. 🤖 Chat Handling

* Recognizes small talk (e.g., “Hi”, “What can you do?”) and responds smartly without triggering SQL generation.

### 7. 🖥️ Streamlit Frontend

* The **frontend interface** built with **Streamlit** lets users chat with the assistant interactively, view SQL, explanations, and result tables.

---

## 🧩 System Architecture

```
                ┌──────────────────────────────┐
                │          Streamlit UI        │
                │  (User asks questions)       │
                └──────────────┬───────────────┘
                               │ REST API calls
                               ▼
                ┌──────────────────────────────┐
                │         FastAPI Backend      │
                │    (main.py, chat endpoints) │
                ├──────────────────────────────┤
                │ llm_sqlgen.py  → Gemini API  │
                │ sql_executor.py → DuckDB      │
                │ cache.py       → Redis Cache  │
                └──────────────┬───────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │          DuckDB              │
                │  (Ingested Olist Dataset)    │
                └──────────────────────────────┘
```

---

## 🧠 Architecture Components Explained

### **Frontend:** Streamlit

* Simple chat interface.
* Displays questions, generated SQL, explanation, and query results.

### **Backend Framework:** FastAPI

* Exposes REST endpoints `/chat`, `/run_sql`, `/session/{id}`.
* Handles both small talk and analytical queries.

### **Database Layer:** DuckDB

* Lightweight, embedded analytical database.
* Stores ingested CSV data for fast querying.
* Created using `ingest.py`.

### **LLM Integration:** Google Gemini

* Converts natural-language queries to SQL and provides human-readable explanations.

### **Caching Layer:** Redis

* Stores frequently asked questions and chat sessions.
* Reduces LLM and database load.

---

## 💡 Example Queries

| User Question                                     | SQL Output                                                                                                      | Explanation                                       |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| "What was the total number of orders in 2018?"    | `SELECT COUNT(order_id) FROM orders_full WHERE order_purchase_timestamp BETWEEN '2018-01-01' AND '2018-12-31';` | Counts all orders placed during 2018.             |
| "Which product categories had the highest sales?" | SQL query grouping by product_category_name                                                                     | Lists top categories ranked by total sales value. |
| "Show me average delivery time for each state"    | Joins order and geolocation tables                                                                              | Displays mean delivery duration per region.       |

---

## 🧰 Tools and Technologies

| Category               | Tool/Library                             | Purpose                                    |
| ---------------------- | ---------------------------------------- | ------------------------------------------ |
| Frontend               | **Streamlit**                            | Interactive web interface                  |
| Backend Framework      | **FastAPI**                              | API routing and orchestration              |
| LLM                    | **Google Gemini API (via google-genai)** | Natural language → SQL and explanations    |
| Database               | **DuckDB**                               | Analytical database to store Olist dataset |
| Cache                  | **Redis**                                | Query/session caching                      |
| Data Handling          | **pandas**, **pathlib**                  | CSV reading and data management            |
| Environment Management | **dotenv**                               | Load `.env` configuration                  |
| Language               | **Python 3.9+**                          | Core programming language                  |

---

## 🧩 Code Modules Overview

| File              | Functionality                                                             |
| ----------------- | ------------------------------------------------------------------------- |
| `cache.py`        | Handles caching of query results and session chat logs using Redis        |
| `ingest.py`       | Loads all CSVs into DuckDB tables and creates a joined view `orders_full` |
| `llm_sqlgen.py`   | Uses Gemini to generate SQL and a simple explanation                      |
| `sql_executor.py` | Executes SQL safely on DuckDB and returns results as a pandas DataFrame   |
| `main.py`         | Defines FastAPI endpoints, integrates caching, LLM, and SQL executor      |

---

## ⚙️ Environment Setup

### 🧾 `.env.example`

```bash
# .env.example - copy to .env and fill values (do NOT commit .env)

GEMINI_API_KEY=
GEMINI_MODEL=models/gemini-2.5-pro

# Backend URL used by frontend (default)
BACKEND_URL=https://ai-moller-project.onrender.com/

# Redis (use Docker default or local)
REDIS_URL=

# DuckDB path (optional)
DUCKDB_PATH=olist.duckdb
```

---

## 🧭 How to Run Locally

### 1. **Clone the Repository**

```bash
git clone https://github.com/geethz2908/ai_moller_project.git
cd ai_moller_project
```

### 2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 3. **Set Up Environment Variables**

Create a `.env` file at the project root and copy contents from `.env.example`.
Fill in your API key and Redis URL as needed.

### 4. **Ingest the Dataset**

Download the CSVs from [Kaggle Olist Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/)
Place them in a folder called `data/` at the repo root, then run:

```bash
python backend/ingest.py
```

### 5. **Start the Backend**

```bash
uvicorn backend.main:app --reload
```

### 6. **Run the Frontend**

```bash
streamlit run frontend/app.py
```

> The app will open in your browser.
> You can also access the deployed version at [https://ai-moller-project.onrender.com/](https://ai-moller-project.onrender.com/).

---

## 🔭 If I Had More Time

If given more time, I would:

* Add **data visualizations** (charts and graphs) for query results.
* Add **user authentication** and personalized dashboards.
* Optimize caching and enable **multi-user chat sessions**.


## 👩‍💻 Author

**Geethz**
B.Tech AIML, PES University
