from functools import wraps
from fastapi import HTTPException, WebSocket
from .utils import Params, match_key, get_access_token
from ..utils import TokenCriptografy


def websocket_middleware(func):
    @wraps(func)
    async def wrapper(websocket: WebSocket, *args, **kwargs):
        # params = Params(websocket)
        # client_id = params.get_param("client_id")
        access_token = websocket.headers.get("ACCESS-TOKEN")

        try:
            payload: dict | None = TokenCriptografy.decode(access_token)
        except Exception as e:
            await disconnect(websocket=websocket)

        client_id = payload.get("client_id")
        client_key = get_access_token(client_id)

        if access_token is None or not match_key(access_token, client_key):
            await disconnect(websocket=websocket)

        return await func(websocket, *args, **kwargs)

    return wrapper


async def disconnect(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json(
        {"status": "disconnected", "detail": "Unauthrized ACCESS-TOKEN"}
    )
    await websocket.close(code=1008)
    raise HTTPException(status_code=401, detail="Unauthrized ACCESS-TOKEN")
