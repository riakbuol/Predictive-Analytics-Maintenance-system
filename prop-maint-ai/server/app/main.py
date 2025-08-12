from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .config import settings
from .database import Base, engine
from .routers import auth, tenant, admin, predictions, files


def create_app() -> FastAPI:
    app = FastAPI(title="Property Predictive Maintenance API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(tenant.router)
    app.include_router(admin.router)
    app.include_router(predictions.router)
    app.include_router(files.router)

    os.makedirs("uploads", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    static_dir = os.path.join(os.path.dirname(__file__), "static_frontend")
    if os.path.isdir(static_dir):
        app.mount("/app", StaticFiles(directory=static_dir, html=True), name="app")

    @app.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()