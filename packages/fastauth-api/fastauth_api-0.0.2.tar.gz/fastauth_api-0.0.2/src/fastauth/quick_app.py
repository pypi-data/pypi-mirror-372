from fastapi import FastAPI, APIRouter
from .middleware import AccessTokenMiddleware
from .openapi import FastauthOpenAPI
from .routers import TokenRouter


def set_auth(
    fastapp: FastAPI,
    routers: list[APIRouter] = [TokenRouter().route],
) -> None:
    """
    Configure authentication for a FastAPI application.
    Adds AccessTokenMiddleware, installs FastauthOpenAPI, and includes the given routers.

    Args:
        fastapp : FastAPI
            The FastAPI application to configure.
        routers : list[APIRouter], optional
            Routers to include (default: TokenRouter().route).
    
    """
    fastapp.add_middleware(AccessTokenMiddleware)
    openapi: FastauthOpenAPI = FastauthOpenAPI(app=fastapp)
    fastapp.openapi = lambda: openapi()
    for router in routers:
        fastapp.include_router(router=router)
