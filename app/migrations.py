from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def _column_names(engine: Engine, table_name: str) -> set[str]:
    return {column["name"] for column in inspect(engine).get_columns(table_name)}


def ensure_schema_compatibility(engine: Engine) -> None:
    """Apply the additive Phase 6 schema bridge for existing local MVP databases."""

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    statements: list[str] = []

    if "runbooks" in tables:
        runbook_columns = _column_names(engine, "runbooks")
        additions = {
            "mode": "VARCHAR(20) NOT NULL DEFAULT 'automated'",
            "instructions": "TEXT",
            "steps": "TEXT",
            "required_context": "VARCHAR(20) NOT NULL DEFAULT 'none'",
            "risk_level": "VARCHAR(20) NOT NULL DEFAULT 'low'",
            "automation_key": "VARCHAR(120)",
        }
        statements.extend(
            f"ALTER TABLE runbooks ADD COLUMN {name} {definition}"
            for name, definition in additions.items()
            if name not in runbook_columns
        )

    if "incidents" in tables and "updated_at" not in _column_names(engine, "incidents"):
        timestamp_type = (
            "TIMESTAMP WITH TIME ZONE" if engine.dialect.name == "postgresql" else "DATETIME"
        )
        statements.append(f"ALTER TABLE incidents ADD COLUMN updated_at {timestamp_type}")
        statements.append(
            "UPDATE incidents SET updated_at = COALESCE(resolved_at, created_at) "
            "WHERE updated_at IS NULL"
        )

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
