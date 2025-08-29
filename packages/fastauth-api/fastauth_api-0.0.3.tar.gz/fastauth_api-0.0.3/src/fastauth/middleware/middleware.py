from fastapi import Request
from http import HTTPStatus
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse

from .utils import Params, get_access_token
from ..config import logger, ConfigServer
from ..utils import TokenCriptografy


class AccessTokenMiddleware(BaseHTTPMiddleware):
    """
    AccessTokenMiddleware: ASGI middleware for validating master and access tokens.

    This middleware intercepts incoming HTTP requests and enforces two layered
    authorization checks when applicable:

    ### 1. Master token check
        - Trigger: require_master_token(request) returns True.
        - Expected header: "master_token".
        - Validation: header value is compared to ConfigServer.MASTER_TOKEN.
        - Failure: returns a JSONResponse with HTTP 401 and detail "Unauthorized Master Token".

    ### 2. Access token check
        - Trigger: require_access_token(request) returns True.
        - Expected header: "ACCESS-TOKEN".
        - Validation flow:
             a. If the header is missing, returns HTTP 401 with detail
                 "Invalid Access Token. Access Token is null".
             b. The token is decoded via TokenCriptografy.decode(access_token). Any
                 decoding error is caught and returned as HTTP 401 with the error text.
             c. The decoded payload must contain "client_id". If missing, returns
                 HTTP 401 with detail "Invalid Access Token".
             d. The middleware retrieves the canonical token for the client via
                 get_access_token(client_id). If that returns None, returns HTTP 401
                 with detail "Invalid Client ID".
             e. If the canonical token does not exactly match the provided access
                 token, returns HTTP 401 with detail "Unauthorized Access Token".

    ### Behavior
    - If neither check applies or both checks pass, the request is forwarded to
      the downstream handler by awaiting call_next(request).
    - The middleware logs incoming request paths (via logger.info).
    - Token decoding exceptions are handled and converted to HTTP 401 responses;
      they do not propagate.

    ### Interface
    - dispatch(self, request: Request, call_next) -> Response
      - request: Starlette/FastAPI Request instance.
      - call_next: callable that receives the request and returns a Response (awaitable).
      - Returns: a Response instance. On authorization failure, returns a JSONResponse
         with status code 401 and a JSON body containing a "detail" message.

    ### Notes and considerations
    - This middleware is asynchronous and intended for ASGI apps (e.g., FastAPI).
    - Header names are expected exactly as "master_token" and "ACCESS-TOKEN".
    - Comparisons are strict equality checks; ensure token formats match exactly.
    """

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
            master_token: str = req.headers.get("master_token")
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
