from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import incidents, health

def create_app() -> FastAPI:
    app = FastAPI(
        title="ERP Incident Triage API",
        description="API for submitting and triaging ERP incidents",
        version="1.0.0",
    )

    # CORS (frontend separated)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(incidents.router, prefix="/api/v1", tags=["Incidents"])

    return app


app = create_app()
