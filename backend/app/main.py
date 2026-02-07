"""FastAPI application factory for the ERP Incident Triage API."""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1 import incidents, health
from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.request_context import RequestContextMiddleware

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    cloudwatch_handler = setup_logging(settings)

    app = FastAPI(
        title="ERP Incident Triage API",
        description="API for submitting and triaging ERP incidents",
        version="1.0.0",
    )

    app.state.cloudwatch_handler = cloudwatch_handler

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        logger.exception("Database error: %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=503,
            content={"detail": "Database unavailable"},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled error: %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    # CORS (frontend separated)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestContextMiddleware)

    # Register routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(incidents.router, prefix="/api/v1", tags=["Incidents"])

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        handler = getattr(app.state, "cloudwatch_handler", None)
        if handler is not None:
            try:
                handler.close()
            except Exception:
                pass
        logging.shutdown()

    return app


app = create_app()
