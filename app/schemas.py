from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ServiceStatus = Literal["healthy", "degraded", "down", "unknown"]
AlertSeverity = Literal["info", "warning", "critical"]
AlertStatus = Literal["new", "acknowledged", "resolved"]
IncidentSeverity = Literal["low", "medium", "high", "critical"]
IncidentStatus = Literal["open", "investigating", "resolved"]
RunbookMode = Literal["manual", "automated"]
RunbookContext = Literal["none", "service", "incident"]
RunbookRisk = Literal["low", "medium", "high"]
RunbookExecutionStatus = Literal["success", "failed"]


class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    slug: str = Field(
        ...,
        min_length=1,
        max_length=120,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    description: str | None = None
    environment: str = Field(..., min_length=1, max_length=50)
    status: ServiceStatus = "unknown"
    owner: str | None = Field(default=None, max_length=120)


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    description: str | None = None
    environment: str | None = Field(default=None, min_length=1, max_length=50)
    status: ServiceStatus | None = None
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
    owner: str | None = Field(default="Dyllan", max_length=120)


class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    severity: IncidentSeverity | None = None
    owner: str | None = Field(default=None, max_length=120)


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus


class IncidentRead(IncidentCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class RunbookFields(BaseModel):
    name: str = Field(..., min_length=1, max_length=160)
    description: str | None = None
    mode: RunbookMode = "manual"
    instructions: str | None = None
    steps: list[str] = Field(default_factory=list, max_length=20)
    required_context: RunbookContext = "none"
    risk_level: RunbookRisk = "low"
    automation_key: str | None = Field(default=None, max_length=120)
    enabled: bool = True

    @model_validator(mode="after")
    def validate_mode(self):
        self.steps = [step.strip() for step in self.steps if step.strip()]
        if self.mode == "manual" and self.automation_key is not None:
            raise ValueError("A manual runbook cannot define an automation key.")
        if self.mode == "automated" and not self.automation_key:
            raise ValueError("An automated runbook requires an approved automation key.")
        return self


class RunbookCreate(RunbookFields):
    key: str = Field(
        ...,
        min_length=1,
        max_length=120,
        pattern=r"^[a-z0-9]+(?:[_-][a-z0-9]+)*$",
    )


class RunbookUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    instructions: str | None = None
    steps: list[str] | None = Field(default=None, max_length=20)
    required_context: RunbookContext | None = None
    risk_level: RunbookRisk | None = None
    enabled: bool | None = None


class RunbookRead(RunbookFields):
    id: int
    key: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RunbookExecutionRequest(BaseModel):
    service_id: int | None = None
    incident_id: int | None = None
    requested_by: str = Field(default="Dyllan", min_length=1, max_length=120)
    outcome: RunbookExecutionStatus | None = None
    notes: str | None = Field(default=None, max_length=4000)
    completed_steps: list[int] = Field(default_factory=list)


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
