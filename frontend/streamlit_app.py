import os
import httpx
import streamlit as st
import pandas as pd
import plotly.express as px

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(
    page_title="Text-to-SQL Enterprise",
    page_icon="▎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@400;500&display=swap');

:root {
    --primary: #17171c;
    --canvas: #ffffff;
    --ink: #212121;
    --muted: #93939f;
    --slate: #75758a;
    --hairline: #d9d9dd;
    --coral: #ff7759;
    --deep-green: #003c33;
    --action-blue: #1863dc;
    --soft-stone: #eeece7;
    --pale-green: #edfce9;
    --focus-blue: #4c6ee6;
}

/* Force global text and background colors */
html, body, [class*="css"], [data-testid="stApp"] {
    font-family: 'Inter', ui-sans-serif, system-ui, sans-serif !important;
    color: var(--ink) !important;
    background-color: var(--canvas) !important;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: var(--canvas) !important;
    border-right: 1px solid var(--hairline) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
[data-testid="stSidebar"] span, 
[data-testid="stSidebar"] label {
    color: var(--ink) !important;
}

/* Radio buttons labels in Sidebar */
div[data-testid="stRadio"] label {
    color: var(--ink) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 400 !important;
}

div[data-testid="stRadio"] label p {
    color: var(--ink) !important;
}

/* Headings Split (Display vs UI) */
h1, h2, h3, [data-testid="stHeader"] {
    font-family: 'Space Grotesk', ui-sans-serif, sans-serif !important;
    font-weight: 500 !important;
    letter-spacing: -0.02em !important;
    color: var(--primary) !important;
}

h1 { font-size: 2.5rem !important; line-height: 1.1 !important; }
h2 { font-size: 1.75rem !important; line-height: 1.2 !important; }
h3 { font-size: 1.25rem !important; line-height: 1.3 !important; }

/* Text Inputs and Text Areas */
div[data-testid="stTextInput"] input, 
div[data-testid="stTextArea"] textarea {
    background-color: var(--canvas) !important;
    color: var(--ink) !important;
    border: 1px solid var(--hairline) !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}

/* Custom style for the main Query input: Make it a Pill shape */
div[data-testid="stTextInput"]:first-of-type input {
    border-radius: 32px !important;
    padding: 12px 24px !important;
}

div[data-testid="stTextInput"] input:focus, 
div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--focus-blue) !important;
    box-shadow: 0 0 0 2px rgba(76, 110, 230, 0.15) !important;
}

/* Primary Button Styling */
div.stButton > button {
    background-color: var(--primary) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 32px !important;
    padding: 8px 28px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    transition: opacity 0.15s !important;
}

div.stButton > button:hover {
    opacity: 0.85 !important;
    color: #ffffff !important;
    border: none !important;
}

/* Secondary Button Styling */
div.stButton > button[kind="secondary"] {
    background-color: transparent !important;
    color: var(--primary) !important;
    border: 1px solid var(--hairline) !important;
}

/* Metric Cards */
.metric-card {
    background-color: var(--canvas) !important;
    border: 1px solid var(--hairline) !important;
    border-radius: 8px !important;
    padding: 20px !important;
    text-align: center !important;
}

.metric-value {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 500 !important;
    color: var(--primary) !important;
}

.metric-label {
    font-size: 13px !important;
    color: var(--muted) !important;
    margin-top: 4px !important;
}

/* Code and SQL blocks */
.sql-block {
    background-color: var(--soft-stone) !important;
    color: var(--ink) !important;
    border: 1px solid var(--hairline) !important;
    border-radius: 8px !important;
    padding: 16px !important;
    font-family: 'JetBrains Mono', 'SF Mono', monospace !important;
    font-size: 13px !important;
    overflow-x: auto !important;
    white-space: pre-wrap !important;
    line-height: 1.5 !important;
}

/* Explanation Box */
.explanation-box {
    background-color: var(--pale-green) !important;
    color: var(--ink) !important;
    border-radius: 8px !important;
    padding: 16px !important;
    font-size: 15px !important;
    line-height: 1.5 !important;
    border-left: 3px solid var(--deep-green) !important;
}

/* Dataframe Borders */
.stDataFrame {
    border: 1px solid var(--hairline) !important;
    border-radius: 8px !important;
}

/* Hide header default Streamlit styling */
[data-testid="stHeader"] {
    background-color: transparent !important;
}

footer { display: none !important; }
</style>
""", unsafe_allow_html=True)


def api_post(path: str, data: dict = None):
    with httpx.Client(base_url=API_BASE, timeout=30) as client:
        resp = client.post(path, json=data or {})
        resp.raise_for_status()
        return resp.json()


def api_get(path: str, params: dict = None):
    with httpx.Client(base_url=API_BASE, timeout=30) as client:
        resp = client.get(path, params=params or {})
        resp.raise_for_status()
        return resp.json()


def extract_sqlite_schema(db_path: str) -> list[dict]:
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if row[0] not in ('sqlite_sequence',)]
        
        schema_tables = []
        for table_name in tables:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = []
            for col_row in cursor.fetchall():
                columns.append({
                    "name": col_row[1],
                    "type": col_row[2],
                    "pk": bool(col_row[5]),
                    "nullable": not bool(col_row[3])
                })
                
            cursor.execute(f"PRAGMA foreign_key_list({table_name});")
            fk_list = cursor.fetchall()
            for fk_row in fk_list:
                from_col = fk_row[3]
                to_table = fk_row[2]
                to_col = fk_row[4]
                for col in columns:
                    if col["name"] == from_col:
                        col["fk"] = f"{to_table}.{to_col}"
                        
            schema_tables.append({
                "name": table_name,
                "description": f"Table: {table_name}",
                "columns": columns
            })
        conn.close()
        return schema_tables
    except Exception as e:
        st.error(f"Failed to inspect database schema: {e}")
        return []


if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None
if "db_path" not in st.session_state:
    st.session_state.db_path = ""


def run_query():
    text = st.session_state.query_input.strip()
    if not text:
        return
    with st.spinner("Generating SQL..."):
        try:
            payload = {"text": text}
            if st.session_state.db_path:
                payload["db_path"] = st.session_state.db_path
            resp = api_post("/api/query", payload)
            st.session_state.result = resp
            st.session_state.history.append(resp)
        except Exception as e:
            st.error(f"Request failed: {e}")


with st.sidebar:
    st.markdown('<div style="margin-bottom: 32px;">', unsafe_allow_html=True)
    st.markdown('<span style="font-size: 1.5rem; font-weight: 500; letter-spacing: -0.03em; color: var(--primary);">▎ Text→SQL</span>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<p style="font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 8px;">Navigation</p>', unsafe_allow_html=True)
    page = st.radio("", ["Query", "History", "Schema Explorer", "Database Explorer"], label_visibility="collapsed")

    st.markdown("<hr style='margin: 24px 0; border-color: var(--hairline);'>", unsafe_allow_html=True)
    st.markdown('<p style="font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 8px;">Database File</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload SQLite Database (.db, .sqlite, .sql)", type=["db", "sqlite", "sqlite3", "sql"], label_visibility="collapsed")
    if uploaded_file is not None:
        os.makedirs("uploaded_dbs", exist_ok=True)
        
        if uploaded_file.name.endswith(".sql"):
            db_name = uploaded_file.name.rsplit(".", 1)[0] + ".db"
            saved_path = os.path.abspath(os.path.join("uploaded_dbs", db_name))
        else:
            saved_path = os.path.abspath(os.path.join("uploaded_dbs", uploaded_file.name))
        
        # Only save and index if it's a new file or hasn't been indexed
        if st.session_state.db_path != saved_path:
            if uploaded_file.name.endswith(".sql"):
                sql_script = uploaded_file.getvalue().decode("utf-8")
                import sqlite3
                if os.path.exists(saved_path):
                    try:
                        os.remove(saved_path)
                    except Exception:
                        pass
                try:
                    conn = sqlite3.connect(saved_path)
                    conn.executescript(sql_script)
                    conn.commit()
                    conn.close()
                except Exception as e:
                    st.error(f"Failed to build database from SQL script: {e}")
                    saved_path = None
            else:
                with open(saved_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            if saved_path:
                with st.spinner("Extracting & Indexing Schema..."):
                    schema = extract_sqlite_schema(saved_path)
                    if schema:
                        try:
                            api_post("/api/schema/index", {"tables": schema})
                            st.toast("Schema indexed successfully!")
                        except Exception as e:
                            st.error(f"Failed to index schema: {e}")
                
                st.session_state.db_path = saved_path
                st.success(f"Loaded: {uploaded_file.name}")
    
    st.markdown('<p style="font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 16px; margin-bottom: 8px;">Custom DB Path</p>', unsafe_allow_html=True)
    db_path_input = st.text_input("DB Path", value=st.session_state.db_path, placeholder="Leave empty for default", label_visibility="collapsed")
    if db_path_input != st.session_state.db_path:
        st.session_state.db_path = db_path_input

    if page != "Query":
        st.session_state.result = None


if page == "Query":
    st.markdown('<h1>Ask your database</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: var(--slate); font-size: 16px; margin-bottom: 24px;">Describe what you want in plain English, and get SQL + results instantly.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 0.15])
    with col1:
        st.text_input("", placeholder="e.g. Show me the top 5 customers by total revenue this year", key="query_input", on_change=run_query, label_visibility="collapsed")
    with col2:
        st.button("Generate", on_click=run_query, type="primary")

    if st.session_state.result:
        r = st.session_state.result
        if r.get("error"):
            st.error(f"**Error:** {r['error']}")

        if r.get("explanation"):
            st.markdown(f'<div class="explanation-box">{r["explanation"]}</div>', unsafe_allow_html=True)

        if r.get("sql"):
            st.markdown('<p style="font-size: 13px; color: var(--muted); margin: 16px 0 6px;">Generated SQL</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="sql-block">{r["sql"]}</div>', unsafe_allow_html=True)

        result = r.get("result", {})
        if result.get("columns") and result.get("rows"):
            df = pd.DataFrame(result["rows"])
            st.markdown('<p style="font-size: 13px; color: var(--muted); margin: 16px 0 6px;">Results</p>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{result["row_count"]}</div><div class="metric-label">Rows</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{result["execution_time_ms"]}ms</div><div class="metric-label">Time</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{len(result["columns"])}</div><div class="metric-label">Columns</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{"✓" if r["success"] else "✗"}</div><div class="metric-label">Status</div></div>', unsafe_allow_html=True)

            if result["row_count"] > 0 and len(result["columns"]) >= 2:
                with st.expander("Chart"):
                    chart_type = st.selectbox("Type", ["Bar", "Line", "Scatter", "Pie"])
                    x_col = st.selectbox("X axis", result["columns"])
                    y_opts = [c for c in result["columns"] if c != x_col]
                    if y_opts:
                        y_col = st.selectbox("Y axis", y_opts)
                        fig = None
                        if chart_type == "Bar":
                            fig = px.bar(df, x=x_col, y=y_col)
                        elif chart_type == "Line":
                            fig = px.line(df, x=x_col, y=y_col)
                        elif chart_type == "Scatter":
                            fig = px.scatter(df, x=x_col, y=y_col)
                        elif chart_type == "Pie":
                            fig = px.pie(df, names=x_col, values=y_col)
                        if fig:
                            fig.update_layout(template="plotly_white", margin=dict(t=20, b=20))
                            st.plotly_chart(fig, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Export CSV", csv, "query_results.csv", "text/csv")

elif page == "History":
    st.markdown('<h1>Query History</h1>', unsafe_allow_html=True)
    try:
        entries = api_get("/api/history", {"limit": 50})
        if not entries:
            st.markdown('<p style="color: var(--muted);">No queries yet.</p>', unsafe_allow_html=True)
        for e in entries:
            icon = "✓" if e["success"] else "✗"
            st.markdown(f"""<div class="history-item">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1;">
                        <p style="font-weight: 500; margin: 0;">{e["natural_language"]}</p>
                        <p style="font-size: 13px; color: var(--slate); margin: 4px 0 0; font-family: monospace;">{e["sql_query"][:120]}{"…" if len(e["sql_query"]) > 120 else ""}</p>
                    </div>
                    <div style="text-align: right; flex-shrink: 0; margin-left: 16px;">
                        <span style="font-size: 13px; color: var(--muted);">{e["row_count"]} rows</span>
                        <span style="font-size: 13px; color: var(--muted); margin-left: 8px;">{e["execution_time_ms"]}ms</span>
                        <span style="font-size: 13px; margin-left: 8px;">{icon}</span>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not load history: {e}")

elif page == "Schema Explorer":
    st.markdown('<h1>Schema Explorer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: var(--slate); margin-bottom: 16px;">Search your indexed database schema to understand what the AI knows.</p>', unsafe_allow_html=True)

    q = st.text_input("", placeholder="Search schema (e.g. customer orders)", label_visibility="collapsed")
    if q:
        try:
            resp = api_get("/api/schema/search", {"q": q})
            st.markdown(f'<div class="sql-block">{resp["context"]}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Search failed: {e}")

elif page == "Database Explorer":
    st.markdown('<h1>Database Explorer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: var(--slate); margin-bottom: 16px;">Run raw SQL directly against the database.</p>', unsafe_allow_html=True)

    raw_sql = st.text_area("SQL", placeholder="SELECT * FROM sqlite_master", height=100)
    if st.button("Execute", type="primary") and raw_sql.strip():
        try:
            payload = {"text": f"run: {raw_sql}"}
            if st.session_state.db_path:
                payload["db_path"] = st.session_state.db_path
            resp = api_post("/api/query", payload)
        except Exception as e:
            st.error(f"Execution failed: {e}")
            resp = None

        if resp and resp.get("sql"):
            st.markdown(f'<div class="sql-block">{resp["sql"]}</div>', unsafe_allow_html=True)
            result = resp.get("result", {})
            if result.get("rows"):
                df = pd.DataFrame(result["rows"])
                st.dataframe(df, use_container_width=True, hide_index=True)
