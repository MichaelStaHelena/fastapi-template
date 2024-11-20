import psutil
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Get API health status",
    response_description="Health check information"
)
async def health_check():
    """
    Perform a health check of the API.
    Returns system metrics including CPU and memory usage.
    """
    return {
        "status": "running",
        "system": {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent
        }
    }


@router.get(
    "/health/db",
    summary="Check database connection",
    response_description="Database health status"
)
async def db_health_check(session: Session = Depends(get_session)):
    """
    Check the database connection health.
    Performs a simple query to verify database connectivity.
    """
    try:
        session.exec(select(1)).one()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
