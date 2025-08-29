from fastapi import FastAPI, APIRouter
from .middleware import AccessTokenMiddleware
from .openapi import FastauthOpenAPI
from .routers import TokenRouter
from .config import DatabaseConfig, ConfigServer, TokenConfig
from pydantic import BaseModel


class FastauthSettings(BaseModel):
    app_name: str = "fastauth-api"
    database_api_path: str | None = None
    master_token: str | None = None
    cryptography_key: str | None = None
    headers: dict | None = None
    master_token_paths: list | None = []
    access_token_paths: list | None = []


class Fastauth:
    def __init__(self, settings: FastauthSettings | dict | None = None):
        if isinstance(settings, dict):
            settings = FastauthSettings(**settings)
        self.__update_settings(settings)

    def __update_settings(self, settings: FastauthSettings | None):
        if settings is not None:
            database_path = settings.database_api_path
            master_token = settings.master_token
            cryptography_key = settings.cryptography_key
            headers = settings.headers
            master_token_paths = settings.master_token_paths or []
            access_token_paths = settings.access_token_paths or []

            DatabaseConfig.PATH = database_path or DatabaseConfig.PATH
            ConfigServer.MASTER_TOKEN = master_token or ConfigServer.MASTER_TOKEN
            TokenConfig.CRYPTOGRAPHY_KEY = (
                cryptography_key or TokenConfig.CRYPTOGRAPHY_KEY
            )
            ConfigServer.MASTER_PATHS = master_token_paths + ConfigServer.MASTER_PATHS
            ConfigServer.ACCESS_TOKEN_PATHS = (
                access_token_paths + ConfigServer.ACCESS_TOKEN_PATHS
            )

    def set_auth(
        self,
        fastapp: FastAPI,
        routers: list[APIRouter] = [TokenRouter().route],
    ) -> None:
        """
        Configure authentication for a FastAPI application.
        Adds AccessTokenMiddleware, installs FastauthOpenAPI, and includes the given routers.

        Args:
            fastapp : FastAPI
                The FastAPI application to settingsure.
            routers : list[APIRouter], optional
                Routers to include (default: TokenRouter().route).

        """
        fastapp.add_middleware(AccessTokenMiddleware)
        openapi: FastauthOpenAPI = FastauthOpenAPI(app=fastapp)
        fastapp.openapi = lambda: openapi()
        for router in routers:
            fastapp.include_router(router=router)
