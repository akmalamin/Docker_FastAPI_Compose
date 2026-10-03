from fastapi import APIRouter, status
from datetime import datetime
from app.cache.redis_client import cache

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    db_status = "unknown"
    try:
        from app.db.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        db_status = "healthy ✅"
    except Exception:
        db_status = "unhealthy ❌"

    return {
        "status": "healthy",
        "services": {
            "fastapi": "running ✅",
            "postgresql": db_status,
            "redis": cache.status,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }