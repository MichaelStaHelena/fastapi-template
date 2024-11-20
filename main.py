import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlmodel import SQLModel

from app.config import get_settings
from app.database import engine
from app.logging_config import setup_logging
from app.routers.api import character_router, jutsu_router
from app.routers.health import router as health_router

settings = get_settings()


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting application...")

    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created")

    yield

    logger.info("Shutting down application...")
    if engine is not None:
        engine.dispose()
        logger.info("Database connection closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Project and Task Management API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": error["loc"][-1],
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "errors": errors,
            "path": request.url.path
        }
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Data validation error",
            "errors": errors,
            "path": request.url.path
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "request_id": request.headers.get("X-Request-ID", None)
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred.",
            "request_id": request.headers.get("X-Request-ID", None),
        },
    )


# Include routers
app.include_router(
    character_router,
    prefix=settings.api_v1_prefix
)
app.include_router(
    jutsu_router,
    prefix=settings.api_v1_prefix
)
app.include_router(health_router)


# Root endpoint
@app.get("/",
         summary="Root endpoint",
         description="Returns basic API information",
         tags=["root"]
         )
async def root():
    return {
        "app_name": settings.app_name,
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
