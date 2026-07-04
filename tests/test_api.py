import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    yield


class TestHealth:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestQuery:
    def test_query_no_api_key_returns_message(self):
        resp = client.post("/api/query", json={"text": "show me all users"})
        assert resp.status_code == 200
        data = resp.json()
        assert "sql" in data
        assert "query_id" in data

    def test_query_empty_text_fails(self):
        resp = client.post("/api/query", json={"text": ""})
        assert resp.status_code == 422

    def test_explain_endpoint(self):
        resp = client.post("/api/explain", json={"text": "SELECT * FROM users"})
        assert resp.status_code == 200
        assert "explanation" in resp.json()

    def test_optimize_endpoint(self):
        resp = client.post("/api/optimize", json={"text": "SELECT * FROM users"})
        assert resp.status_code == 200
        assert "suggestions" in resp.json()


class TestHistory:
    def test_history_empty(self):
        resp = client.get("/api/history")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_history_after_query(self):
        client.post("/api/query", json={"text": "show users"})
        resp = client.get("/api/history", params={"limit": 5})
        data = resp.json()
        assert len(data) >= 1
        assert "natural_language" in data[0]


class TestSchema:
    def test_schema_search_no_index(self):
        resp = client.get("/api/schema/search", params={"q": "users"})
        assert resp.status_code == 200
        assert "context" in resp.json()

    def test_schema_index_and_search(self):
        tables = [
            {
                "name": "customers",
                "description": "Customer records",
                "columns": [
                    {"name": "id", "type": "INTEGER", "pk": True},
                    {"name": "name", "type": "TEXT"},
                    {"name": "email", "type": "TEXT"},
                ],
            }
        ]
        resp = client.post("/api/schema/index", json={"tables": tables})
        assert resp.status_code == 200

        resp = client.get("/api/schema/search", params={"q": "customer email"})
        assert resp.status_code == 200
        assert "customers" in resp.json()["context"]
