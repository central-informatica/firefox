"""
XSecurity-Vault - Microservices Orchestrator

This is the main entry point for the XSecurity-Vault backend,
which orchestrates the following microservices:
- Auth (port 8001): Authentication, users, organizations
- Cofre (port 8002): Certificate encryption, storage, signing
- KMS (port 8000): Key management (used by Cofre)

XSecurity-Vault handles:
- Business logic (grupos, planos, regras, empresas)
- Multi-tenant management
- Access control rules
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import FRONTEND_ORIGINS
from backend.app.core.exceptions import (
    CircuitBreakerOpenError,
    ServiceError,
    ServiceTimeoutError,
    ServiceUnavailableError,
)

# Service clients
from backend.app.services.auth_client import auth_client
from backend.app.services.cofre_client import cofre_client

# Routers - Authentication (proxied to Auth service)
from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.usuarios import router as usuarios_router
from backend.app.api.routes.convites import router as convites_router
from backend.app.api.routes.companies import router as companies_router
from backend.app.api.routes.certificados import router as certificados_router

# Routers - Business logic (local)
from backend.app.api.routes.grupos import router as grupos_router
from backend.app.api.routes.planos_trabalho import router as planos_trabalho_router
from backend.app.api.routes.feriados import router as feriados_router
from backend.app.api.routes.grupos_certificados import router as grupos_certificados_router
from backend.app.api.routes.grupos_certificados_urls import router as grupos_certificados_urls_router
from backend.app.api.routes.grupos_usuarios import router as grupos_usuarios_router
from backend.app.api.routes.regras_acesso import router as regras_acesso_router
from backend.app.api.routes.usuarios_ip_whitelist import router as usuarios_ip_whitelist_router
from backend.app.api.routes.global_urls import router as global_urls_router
from backend.app.api.routes.ramos import router as ramos_router


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Lifespan - Startup/Shutdown
# -----------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Initializes service clients on startup and closes them on shutdown.
    """
    # Startup
    logger.info("Starting XSecurity-Vault orchestrator...")

    # Initialize service clients
    await auth_client.initialize()
    logger.info("Auth client initialized")

    await cofre_client.initialize()
    logger.info("Cofre client initialized")

    # Check service health
    auth_healthy = await auth_client.health_check()
    cofre_healthy = await cofre_client.health_check()

    if not auth_healthy:
        logger.warning("Auth service is not healthy!")
    if not cofre_healthy:
        logger.warning("Cofre service is not healthy!")

    logger.info("XSecurity-Vault started successfully")

    yield

    # Shutdown
    logger.info("Shutting down XSecurity-Vault...")

    await auth_client.close()
    await cofre_client.close()

    logger.info("XSecurity-Vault shutdown complete")


# -----------------------------------------------------------------------------
# Application
# -----------------------------------------------------------------------------

app = FastAPI(
    title="XSecurity-Vault",
    description="Secure digital certificate management orchestrator",
    version="2.0.0",
    lifespan=lifespan,
)


# -----------------------------------------------------------------------------
# CORS Middleware
# -----------------------------------------------------------------------------

# Use origins from environment configuration
# Fall back to localhost for development if not configured
origins = FRONTEND_ORIGINS if FRONTEND_ORIGINS else [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

# Explicitly whitelist HTTP methods instead of using "*"
ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

# Explicitly whitelist headers instead of using "*"
ALLOWED_HEADERS = [
    "Authorization",
    "Content-Type",
    "X-CSRF-Token",
    "X-Requested-With",
    "Accept",
    "Origin",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)


# -----------------------------------------------------------------------------
# Exception Handlers
# -----------------------------------------------------------------------------


@app.exception_handler(ServiceUnavailableError)
async def service_unavailable_handler(
    request: Request,
    exc: ServiceUnavailableError,
) -> JSONResponse:
    """Handle service unavailable errors."""
    logger.error(f"Service unavailable: {exc}")
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Servico temporariamente indisponivel",
            "service": exc.service_name,
        },
    )


@app.exception_handler(ServiceTimeoutError)
async def service_timeout_handler(
    request: Request,
    exc: ServiceTimeoutError,
) -> JSONResponse:
    """Handle service timeout errors."""
    logger.error(f"Service timeout: {exc}")
    return JSONResponse(
        status_code=504,
        content={
            "detail": "Servico demorou muito para responder",
            "service": exc.service_name,
        },
    )


@app.exception_handler(CircuitBreakerOpenError)
async def circuit_breaker_handler(
    request: Request,
    exc: CircuitBreakerOpenError,
) -> JSONResponse:
    """Handle circuit breaker open errors."""
    logger.warning(f"Circuit breaker open: {exc}")
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Servico temporariamente bloqueado, tente novamente em breve",
            "service": exc.service_name,
            "retry_after": exc.detail.get("retry_after", 30),
        },
    )


@app.exception_handler(ServiceError)
async def service_error_handler(
    request: Request,
    exc: ServiceError,
) -> JSONResponse:
    """Handle generic service errors."""
    logger.error(f"Service error: {exc}")
    return JSONResponse(
        status_code=exc.status_code or 500,
        content={
            "detail": exc.message,
            "service": exc.service_name,
        },
    )


# -----------------------------------------------------------------------------
# Routers
# -----------------------------------------------------------------------------

# Authentication (proxied to Auth service)
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(convites_router)
app.include_router(companies_router)
app.include_router(certificados_router)

# Business logic (local)
app.include_router(grupos_router)
app.include_router(grupos_certificados_router)
app.include_router(grupos_certificados_urls_router)
app.include_router(grupos_usuarios_router)
app.include_router(planos_trabalho_router)
app.include_router(feriados_router)
app.include_router(regras_acesso_router)
app.include_router(usuarios_ip_whitelist_router)
app.include_router(global_urls_router)
app.include_router(ramos_router)


# -----------------------------------------------------------------------------
# Health Endpoints
# -----------------------------------------------------------------------------


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "XSecurity-Vault",
        "version": "2.0.0",
        "status": "running",
        "description": "Microservices orchestrator for secure certificate management",
    }


@app.get("/health")
async def health():
    """
    Health check endpoint.

    Returns status of all connected services.
    """
    auth_healthy = await auth_client.health_check()
    cofre_healthy = await cofre_client.health_check()

    all_healthy = auth_healthy and cofre_healthy

    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": {
            "auth": {
                "status": "healthy" if auth_healthy else "unhealthy",
                "url": auth_client.base_url,
            },
            "cofre": {
                "status": "healthy" if cofre_healthy else "unhealthy",
                "url": cofre_client.base_url,
            },
        },
    }


@app.get("/ready")
async def ready():
    """
    Readiness probe.

    Returns 200 if the application is ready to handle requests.
    """
    # Check if service clients are initialized
    try:
        _ = auth_client.client
        _ = cofre_client.client
        return {"status": "ready"}
    except RuntimeError:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "detail": "Service clients not initialized"},
        )


@app.get("/live")
async def live():
    """
    Liveness probe.

    Returns 200 if the application is running.
    """
    return {"status": "alive"}
