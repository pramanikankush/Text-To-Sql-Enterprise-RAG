# Text-to-SQL Enterprise UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the Streamlit frontend for Text-to-SQL Enterprise to align with the Cohere 2026 Web System design language, resolving invisible text, dark inputs, and styling mismatches by creating a global Streamlit config and writing custom high-specificity CSS overrides.

**Architecture:** Create a `.streamlit/config.toml` file to force Streamlit's engine into light mode globally. Add high-specificity CSS overrides to `frontend/streamlit_app.py` to target text, headers, sidebars, text inputs, radio buttons, buttons, metric cards, SQL blocks, and explanation containers, ensuring they use Cohere's color scheme and radii.

**Tech Stack:** Streamlit, Python, CSS

---

### Task 1: Create Streamlit Theme Configuration

**Files:**
- Create: `.streamlit/config.toml`

- [ ] **Step 1: Create Streamlit configuration directory and write config file**

Write the following content to `c:/Users/ankus/Desktop/portfolio projects/Text-to-SQL-Enterprise/.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#17171c"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#eeece7"
textColor = "#212121"
font = "sans serif"

[server]
headless = true
```

- [ ] **Step 2: Verify file creation and contents**

Check that `.streamlit/config.toml` has been created and contains the correct configuration.

---

### Task 2: Inject Custom CSS Overrides in Streamlit App

**Files:**
- Modify: `frontend/streamlit_app.py:16-169`

- [ ] **Step 1: Rewrite CSS overrides block in `frontend/streamlit_app.py`**

Replace the existing `st.markdown("""<style>...</style>""", unsafe_allow_html=True)` block with the following comprehensive design-compliant styling:

```python
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
```

---

### Task 3: Verify and Run Application

**Files:**
- Run commands in terminal to check backend and frontend integration.

- [ ] **Step 1: Run the backend test suite**

Run: `pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 2: Start backend FastAPI server**

Run: `uvicorn app.main:app --reload`
Check console logs to ensure the database initializes correctly.

- [ ] **Step 3: Start frontend Streamlit application**

Run: `streamlit run frontend/streamlit_app.py`
Verify that the application launches on port 8501 without errors.
