from fastapi import Request
from http import HTTPStatus
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse

from .utils import Params, get_access_token
from ..config import logger, ConfigServer
from ..utils import TokenCriptografy


class AccessTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, req: Request, call_next) -> Response:
        logger.info(f"Request Path: {req.url.path}")

        check_master: Response | None = self.__check_master(req=req)
        if check_master is not None:
            return check_master

        check_access: Response | None = self.__check_access(req=req)
        if check_access is not None:
            return check_access

        return await call_next(req)

    def __check_master(self, req: Request) -> Response | None:
        if require_master_token(req):
            master_token: str = req.headers.get("MASTER-TOKEN")
            required_token: str = ConfigServer.MASTER_TOKEN

            if master_token != required_token or master_token is None:
                return JSONResponse(
                    content={"detail": "Unauthorized Master Token"},
                    status_code=HTTPStatus.UNAUTHORIZED,
                )

        return None

    def __check_access(self, req: Request) -> Response | None:
        if require_access_token(req):
            # client_id: str | None = Params(req).get_param("client_id")
            access_token: str = req.headers.get("ACCESS-TOKEN")
            if access_token is None:
                return JSONResponse(
                    content={"detail": "Invalid Access Token. Access Token is null"},
                    status_code=HTTPStatus.UNAUTHORIZED,
                )
            payload: dict = {}
            try:
                payload = TokenCriptografy.decode(access_token)
            except Exception as e:
                return JSONResponse(
                    content={"detail": f"Invalid Access Token. Error: {e}"},
                    status_code=HTTPStatus.UNAUTHORIZED,
                )

            client_id: str | None = payload.get("client_id")
            required_token: str = get_access_token(client_id)

            if required_token is None:
                return JSONResponse(
                    content={"detail": "Invalid Client ID"},
                    status_code=HTTPStatus.UNAUTHORIZED,
                )
            if client_id is None:
                return JSONResponse(
                    content={"detail": "Invalid Access Token"},
                    status_code=HTTPStatus.UNAUTHORIZED,
                )

            if required_token != access_token:
                return JSONResponse(
                    content={"detail": "Unauthorized Access Token"},
                    status_code=HTTPStatus.UNAUTHORIZED,
                )

        return None


def require_master_token(req: Request) -> bool:
    for path in ConfigServer.MASTER_PATHS:
        if req.url.path.startswith(path):
            return True
    return False


def require_access_token(req: Request) -> bool:
    for path in ConfigServer.ACCESS_TOKEN_PATHS:
        if req.url.path.startswith(path):
            return True
    return False
