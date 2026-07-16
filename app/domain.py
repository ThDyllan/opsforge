from __future__ import annotations

import json
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from .models import AuditLog


DEFAULT_OPERATOR = "Dyllan"

ALERT_TRANSITIONS: dict[str, set[str]] = {
    "new": {"acknowledged", "resolved"},
    "acknowledged": {"resolved"},
    "resolved": set(),
}

INCIDENT_TRANSITIONS: dict[str, set[str]] = {
    "open": {"investigating"},
    "investigating": {"resolved"},
    "resolved": set(),
}


def operator_from_request(request: Request) -> str:
    actor = request.headers.get("X-OpsForge-Actor", "").strip()
    return actor[:120] or DEFAULT_OPERATOR


def json_text(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def add_audit_log(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: int | None,
    actor: str,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    log = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor=actor,
        details=json_text(details or {}),
    )
    db.add(log)
    return log


def transition_allowed(
    transitions: dict[str, set[str]], current: str, target: str
) -> bool:
    return target == current or target in transitions.get(current, set())
