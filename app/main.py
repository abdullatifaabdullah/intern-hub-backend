import sys
import asyncio
import traceback
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.internships import router as internships_router
from app.routes.applications import router as applications_router
from app.core.preflight import run_preflight_checks
from app.core.bootstrap import check_db_initialized, bootstrap

# Import all models to ensure Base.metadata includes all tables
from app.models.user import User  # noqa: F401
from app.models.internship import Internship  # noqa: F401
from app.models.application import Application  # noqa: F401


def create_app() -> FastAPI:
    if sys.platform == "win32":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except Exception:
            pass
    app = FastAPI(title="InternHub API", version="2.0.0")

    # Log CORS configuration for debugging
    print(f"🔧 CORS Origins configured: {settings.CORS_ORIGINS}")

    # Add CORS middleware FIRST (before routers)
    # This ensures CORS headers are added to all responses, including errors
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Add exception handlers to ensure CORS headers on errors
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        response = JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
        # Add CORS headers manually if needed
        origin = request.headers.get("origin")
        if origin in settings.CORS_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        response = JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )
        origin = request.headers.get("origin")
        if origin in settings.CORS_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    # Global exception handler for all unhandled exceptions (500 errors)
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # Log the full traceback for debugging
        print(f"❌ Unhandled exception: {exc}")
        print(f"   Type: {type(exc).__name__}")
        traceback.print_exc()
        
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal server error: {str(exc)}"},
        )
        # Always add CORS headers, even for 500 errors
        origin = request.headers.get("origin")
        if origin in settings.CORS_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
        return response

    app.include_router(auth_router, prefix="/api/v2")
    app.include_router(users_router, prefix="/api/v2")
    app.include_router(internships_router, prefix="/api/v2")
    app.include_router(applications_router, prefix="/api/v2")

    @app.get("/healthz")
    async def healthz():
        return {
            "status": "ok",
            "preflight": bool(settings.ENABLE_PREFLIGHT),
            "db_init_check": bool(settings.ENABLE_DB_INIT_CHECK),
            "bootstrap": bool(settings.ENABLE_BOOTSTRAP),
            "lazy_loading": bool(settings.LAZY_LOADING),
            "stateless_strict": bool(settings.STATELESS_STRICT),
        }

    @app.on_event("startup")
    async def on_startup() -> None:
        # Ordered startup per spec
        if settings.ENABLE_PREFLIGHT:
            await run_preflight_checks()
        if settings.ENABLE_DB_INIT_CHECK:
            await check_db_initialized()
        if settings.ENABLE_BOOTSTRAP:
            await bootstrap()

    return app


app = create_app()

 