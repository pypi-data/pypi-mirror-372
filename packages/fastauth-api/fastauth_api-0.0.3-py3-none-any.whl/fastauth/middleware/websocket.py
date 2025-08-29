from functools import wraps
from fastapi import HTTPException, WebSocket
from enum import Enum
from .utils import Params, match_key, get_access_token
from ..utils import TokenCriptografy
from ..config import logger, ConfigServer


class TokenType(Enum):
    ACCESS = "access"
    MASTER = "master"


def websocket_middleware(token_type: TokenType = TokenType.ACCESS):
    """
    Decorator factory that enforces token-based authentication for FastAPI WebSocket endpoints.
    This decorator inspects incoming WebSocket headers and performs one of two checks before
    allowing the wrapped handler to run:
    - `TokenType.ACCESS` (default): expects header "ACCESS-TOKEN", decodes it, verifies the client_id
        and compares the token against the stored access key. On failure it calls the connection
        disconnect helper and prevents the handler from executing.
    - `TokenType.MASTER`: expects header "master_token" and compares it to ConfigServer.MASTER_TOKEN.
        On mismatch it disconnects the client and prevents handler execution.

    ### Parameters
    `token_type`: `TokenType`
            Token type required for the endpoint (`TokenType.ACCESS` or `TokenType.MASTER`). Defaults to
            `TokenType.ACCESS`.
    ---
    ### Example
    ```python
    # file:api.py
    @app.websocket("/ws/master")
    @websocket_middleware(token_type=TokenType.MASTER)
    async def websocket_chat(websocket: WebSocket):
        await websocket.accept()
        await websocket.send_json({"status": "success","detail": "Connected: Connection Accepted"})
        ...
    ```
    ---
    ### Notes
    - Intended for use with FastAPI WebSocket routes.
    - Keep the wrapped function signature compatible with a FastAPI WebSocket handler
        (first parameter should be a WebSocket).
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(websocket: WebSocket, *args, **kwargs):
            disconnected: bool = False
            if token_type == TokenType.ACCESS:
                token = websocket.headers.get("ACCESS-TOKEN")
                try:
                    payload = TokenCriptografy.decode(token)
                    client_id = payload.get("client_id")
                    client_key = get_access_token(client_id)
                    if token is None or not match_key(token, client_key):
                        await disconnect(websocket=websocket)
                        disconnected = True

                except Exception:
                    await disconnect(websocket=websocket)

            if token_type == TokenType.MASTER:
                token = websocket.headers.get("master_token")
                master_token: str = ConfigServer.MASTER_TOKEN

                if token is None or master_token != token:
                    await disconnect(
                        websocket=websocket,
                        detail="Disconnected: Unauthorized Master Token",
                    )
                    disconnected = True

            if not disconnected:
                return await func(websocket, *args, **kwargs)

        return wrapper

    return decorator


async def disconnect(
    websocket: WebSocket, detail: str = "Disconnected: Unauthrized ACCESS-TOKEN"
):
    await websocket.accept()
    await websocket.send_json({"status": "error", "detail": detail})
    await websocket.close(code=1008)
    raise HTTPException(status_code=401, detail=detail)
