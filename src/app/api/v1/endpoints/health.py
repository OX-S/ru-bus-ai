from fastapi import APIRouter, HTTPException

from src.app.db.session import ping

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", summary="Liveness probe")
def liveness() -> dict[str, str]:
    # Just proves the process can answer HTTP.
    return {"status": "alive"}


@router.get("/ready", summary="Readiness probe")
def readiness() -> dict[str, str]:
    # Verifies the DuckDB file can be opened and queried.
    try:
        ping()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="DuckDB unavailable") from exc

    return {"status": "ready"}
