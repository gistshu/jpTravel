from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.database import create_database_tables
from app.core.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Create database tables during application startup."""
    create_database_tables()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
        lifespan=lifespan,
    )
    register_exception_handlers(application)
    application.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        same_site="lax",
        https_only=False,
    )
    application.include_router(api_router, prefix="/api")
    application.mount("/static", StaticFiles(directory="static"), name="static")

    @application.get("/", include_in_schema=False)
    def get_homepage() -> FileResponse:
        return FileResponse("static/index.html")

    return application


app = create_app()
