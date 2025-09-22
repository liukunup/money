import sentry_sdk

from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from .config import settings
from .routers import system, login, users, private


api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(login.router)
api_router.include_router(users.router)

# Add private routes only in local environment
if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)

# Initialize Sentry only if DSN is provided and environment is not local
if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

srv = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    srv.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

srv.include_router(api_router, prefix=settings.API_V1_STR)
