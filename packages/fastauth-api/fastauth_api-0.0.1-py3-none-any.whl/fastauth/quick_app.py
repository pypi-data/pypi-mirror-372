from fastapi import FastAPI, APIRouter
from .middleware import AccessTokenMiddleware
from .openapi import FastauthOpenAPI
from .routers import TokenRouter


def set_auth(
    fastapp: FastAPI,
    routers: list[APIRouter] = [TokenRouter().route],
) -> None:
    """
    Genera middleware, token routes y openapi automaticamente con los valores default.
    """
    fastapp.add_middleware(AccessTokenMiddleware)
    openapi: FastauthOpenAPI = FastauthOpenAPI(app=fastapp)
    fastapp.openapi = lambda: openapi()
    for router in routers:
        fastapp.include_router(router=router)
