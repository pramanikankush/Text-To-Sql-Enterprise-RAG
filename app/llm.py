import json
from httpx import Client as HttpxClient

from app.config import settings


def generate_sql(natural_language: str, schema_context: str) -> dict:
    prompt = f"""You are a SQL expert. Convert the natural language to a SQL query.

Database schema:
{schema_context}

Natural language: {natural_language}

Return ONLY valid JSON with these keys:
- "sql": the SQL query
- "explanation": short explanation of what the query does
- "dialect": "sqlite" or "postgresql"

Never use UPDATE, DELETE, DROP, INSERT, ALTER, CREATE, or TRUNCATE. Read-only queries only."""
    return _call_groq(prompt)


def explain_sql(sql_query: str) -> str:
    prompt = f"""Explain this SQL query in plain English, step by step:

{sql_query}

Keep it concise, 2-4 sentences."""
    resp = _call_groq(prompt)
    return resp.get("explanation", resp.get("sql", ""))


def optimize_suggestions(sql_query: str) -> str:
    prompt = f"""Review this SQL query for performance improvements.
Suggest 1-2 specific, actionable optimizations (indexing, JOIN order, WHERE clause changes, etc.):

{sql_query}

Keep suggestions brief, one sentence each."""
    resp = _call_groq(prompt)
    return resp.get("explanation", resp.get("sql", ""))


def _call_groq(prompt: str) -> dict:
    if not settings.groq_api_key:
        return {"sql": "SELECT 'Groq API key not configured' AS message", "explanation": "Set GROQ_API_KEY in .env", "dialect": "sqlite"}

    with HttpxClient(timeout=30) as client:
        resp = client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.groq_api_key}", "Content-Type": "application/json"},
            json={
                "model": settings.groq_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
            },
        )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
        content = content.rsplit("```", 1)[0]
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"sql": content, "explanation": "", "dialect": "sqlite"}


def get_embedding(text: str) -> list[float]:
    if not settings.gemini_api_key:
        return [0.0] * 3072
    from google import genai
    client = genai.Client(api_key=settings.gemini_api_key)
    result = client.models.embed_content(model="gemini-embedding-2", contents=text)
    return result.embeddings[0].values
