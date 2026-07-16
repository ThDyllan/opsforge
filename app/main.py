from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .api import router as api_router
from .database import Base, SessionLocal, engine, get_db
from .migrations import ensure_schema_compatibility
from .seed import seed_database
from .web import router as web_router


BASE_DIR = Path(__file__).resolve().parent

HTTP_REQUESTS_TOTAL = Counter(
    "opsforge_http_requests_total",
    "Total HTTP requests handled by OpsForge.",
    ["method", "route", "status_code"],
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "opsforge_http_request_duration_seconds",
    "HTTP request latency in seconds for OpsForge.",
    ["method", "route", "status_code"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_schema_compatibility(engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(title="OpsForge", version="0.2.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(api_router)
app.include_router(web_router)


def _route_label(request: Request) -> str:
    route = request.scope.get("route")
    route_path = getattr(route, "path", None)
    return route_path or "unmatched"


@app.middleware("http")
async def collect_http_metrics(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)

    start_time = perf_counter()
    response = await call_next(request)
    elapsed = perf_counter() - start_time
    labels = {
        "method": request.method,
        "route": _route_label(request),
        "status_code": str(response.status_code),
    }
    HTTP_REQUESTS_TOTAL.labels(**labels).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(**labels).observe(elapsed)
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "opsforge"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is not ready.") from exc
    return {"status": "ready", "service": "opsforge"}


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/overview", status_code=status.HTTP_303_SEE_OTHER)
