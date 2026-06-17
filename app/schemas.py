from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ServiceStatus = Literal["healthy", "degraded", "down", "unknown"]
AlertSeverity = Literal["info", "warning", "critical"]
AlertStatus = Literal["new", "acknowledged", "resolved"]
IncidentSeverity = Literal["low", "medium", "high", "critical"]
IncidentStatus = Literal["open", "investigating", "resolved"]
RunbookExecutionStatus = Literal["success", "failed"]


class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    slug: str = Field(..., min_length=1, max_length=120)
    description: str | None = None
    environment: str = Field(..., min_length=1, max_length=50)
    status: ServiceStatus = "unknown"
    owner: str | None = Field(default=None, max_length=120)


class ServiceRead(ServiceCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertCreate(BaseModel):
    service_id: int | None = None
    source: str = Field(..., min_length=1, max_length=80)
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    severity: AlertSeverity = "info"
    status: AlertStatus = "new"


class AlertRead(AlertCreate):
    id: int
    received_at: datetime
    resolved_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class IncidentCreate(BaseModel):
    service_id: int | None = None
    source_alert_id: int | None = None
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    severity: IncidentSeverity = "medium"
    status: IncidentStatus = "open"
    owner: str | None = Field(default=None, max_length=120)


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus


class IncidentRead(IncidentCreate):
    id: int
    created_at: datetime
    resolved_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class RunbookRead(BaseModel):
    id: int
    key: str
    name: str
    description: str | None
    enabled: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RunbookExecutionRequest(BaseModel):
    service_id: int | None = None
    incident_id: int | None = None
    requested_by: str = Field(default="demo-user", min_length=1, max_length=120)


class RunbookExecutionRead(BaseModel):
    id: int
    runbook_id: int
    service_id: int | None
    incident_id: int | None
    status: RunbookExecutionStatus
    requested_by: str
    output: str
    details: str | None
    started_at: datetime
    finished_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogRead(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: int | None
    actor: str
    details: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
