from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import QueryHistory
from app.llm import generate_sql, explain_sql, optimize_suggestions
from app.chroma_store import index_schema, search_schemas
from core.sql_executor import execute_safe, SQLValidationError

router = APIRouter(prefix="/api")


class NLQuery(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    db_path: str | None = None


class SchemaIndex(BaseModel):
    tables: list[dict]


@router.post("/query")
def query_nl(body: NLQuery, db: Session = Depends(get_db)):
    schema_ctx = search_schemas(body.text)
    llm_result = generate_sql(body.text, schema_ctx)
    sql = llm_result.get("sql", "")
    explanation = llm_result.get("explanation", "")

    try:
        result = execute_safe(sql, body.db_path)
        success = True
        error_msg = ""
    except SQLValidationError as e:
        result = {"columns": [], "rows": [], "row_count": 0, "truncated": False, "execution_time_ms": 0}
        success = False
        error_msg = str(e)
    except Exception as e:
        result = {"columns": [], "rows": [], "row_count": 0, "truncated": False, "execution_time_ms": 0}
        success = False
        error_msg = f"Execution error: {e}"

    history = QueryHistory(
        natural_language=body.text,
        sql_query=sql,
        explanation=explanation,
        result_preview=result.get("rows", [])[:5],
        columns=result.get("columns", []),
        row_count=result.get("row_count", 0),
        execution_time_ms=result.get("execution_time_ms", 0),
        success=success,
        error_message=error_msg,
    )
    db.add(history)
    db.commit()

    return {
        "sql": sql,
        "explanation": explanation,
        "result": result,
        "success": success,
        "error": error_msg if not success else None,
        "query_id": history.id,
    }


@router.post("/explain")
def explain_sql_endpoint(body: NLQuery):
    explanation = explain_sql(body.text)
    return {"sql": body.text, "explanation": explanation}


@router.post("/optimize")
def optimize_sql_endpoint(body: NLQuery):
    suggestions = optimize_suggestions(body.text)
    return {"sql": body.text, "suggestions": suggestions}


@router.post("/schema/index")
def schema_index(body: SchemaIndex):
    index_schema(body.tables)
    return {"status": "ok", "tables_indexed": len(body.tables)}


@router.get("/schema/search")
def schema_search(q: str = ""):
    context = search_schemas(q)
    return {"context": context}


@router.get("/history")
def get_history(limit: int = 20, db: Session = Depends(get_db)):
    entries = (
        db.query(QueryHistory)
        .order_by(desc(QueryHistory.created_at))
        .limit(min(limit, 100))
        .all()
    )
    return [
        {
            "id": e.id,
            "natural_language": e.natural_language,
            "sql_query": e.sql_query,
            "explanation": e.explanation,
            "row_count": e.row_count,
            "execution_time_ms": e.execution_time_ms,
            "success": e.success,
            "error_message": e.error_message,
            "created_at": e.created_at.isoformat(),
        }
        for e in entries
    ]
