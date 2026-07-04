import re
import time
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import sqlparse

from app.config import settings


FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "EXEC", "EXECUTE", "CALL", "ATTACH", "REPLACE",
    "LOAD", "IMPORT", "VACUUM", "REINDEX",
]


class SQLValidationError(Exception):
    pass


def validate_sql(query: str):
    parsed = sqlparse.parse(query)
    if not parsed:
        raise SQLValidationError("Empty or unparseable SQL.")

    normalized = query.strip().upper()
    for kw in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{kw}\b", normalized):
            raise SQLValidationError(f"Forbidden statement: {kw}. Read-only queries only.")

    stmt = parsed[0]
    if stmt.get_type() not in ("SELECT", "UNKNOWN", "EXPLAIN"):
        raise SQLValidationError(f"Only SELECT queries allowed, got {stmt.get_type()}.")

    return True


def execute_safe(query: str, db_path: str | None = None):
    validate_sql(query)

    target_db = db_path or settings.database_url.replace("sqlite:///", "")
    if not Path(target_db).exists():
        target_db = ":memory:"

    start = time.time()
    conn = sqlite3.connect(target_db)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchmany(settings.max_rows + 1)
        truncated = len(rows) > settings.max_rows
        if truncated:
            rows = rows[:settings.max_rows]
        columns = [desc[0] for desc in cur.description] if cur.description else []
        elapsed = int((time.time() - start) * 1000)
        return {
            "columns": columns,
            "rows": [dict(r) for r in rows],
            "row_count": len(rows),
            "truncated": truncated,
            "execution_time_ms": elapsed,
        }
    finally:
        conn.close()
