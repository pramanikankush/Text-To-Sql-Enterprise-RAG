import pytest
from core.sql_executor import validate_sql, SQLValidationError, execute_safe


class TestValidateSQL:
    def test_select_passes(self):
        assert validate_sql("SELECT * FROM users") is True
        assert validate_sql("SELECT name, age FROM users WHERE age > 18") is True

    def test_forbidden_statements(self):
        for kw in ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE"]:
            with pytest.raises(SQLValidationError, match="Forbidden"):
                validate_sql(f"{kw} TABLE users")

    def test_empty_fails(self):
        with pytest.raises(SQLValidationError):
            validate_sql("")


class TestExecuteSafe:
    def test_execute_select(self):
        result = execute_safe("SELECT 1 as val UNION SELECT 2 as val")
        assert result["columns"] == ["val"]
        assert len(result["rows"]) == 2
        assert result["rows"][0]["val"] == 1

    def test_execute_in_memory(self):
        result = execute_safe("SELECT 'hello' AS greeting")
        assert result["rows"][0]["greeting"] == "hello"

    def test_forbidden_raises(self):
        with pytest.raises(SQLValidationError):
            execute_safe("DELETE FROM users")
