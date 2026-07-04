import hashlib
import json

import chromadb

from app.config import settings
from app.llm import get_embedding


def _get_client():
    return chromadb.PersistentClient(path=settings.chroma_persist_dir)


def index_schema(tables: list[dict]):
    client = _get_client()
    try:
        client.delete_collection("schema_store")
    except Exception:
        pass
    collection = client.create_collection("schema_store", metadata={"hnsw:space": "cosine"})

    for table in tables:
        table_text = _table_to_text(table)
        doc_id = hashlib.md5(table["name"].encode()).hexdigest()
        embedding = get_embedding(table_text)
        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[table_text],
            metadatas=[{"table_name": table["name"]}],
        )


def search_schemas(query: str, n_results: int = 5) -> str:
    client = _get_client()
    try:
        collection = client.get_collection("schema_store")
    except Exception:
        return "No schema indexed."

    embedding = get_embedding(query)
    results = collection.query(query_embeddings=[embedding], n_results=n_results)
    if not results["documents"] or not results["documents"][0]:
        return "No matching tables found."
    return "\n\n".join(results["documents"][0])


def _table_to_text(table: dict) -> str:
    lines = [f"Table: {table['name']}"]
    if table.get("description"):
        lines.append(f"Description: {table['description']}")
    for col in table.get("columns", []):
        parts = [f"  - {col['name']} ({col['type']})"]
        if col.get("pk"):
            parts.append("PK")
        if col.get("fk"):
            parts.append(f"FK → {col['fk']}")
        if col.get("nullable") is False:
            parts.append("NOT NULL")
        if col.get("description"):
            parts.append(f": {col['description']}")
        lines.append(" ".join(parts))
    return "\n".join(lines)
