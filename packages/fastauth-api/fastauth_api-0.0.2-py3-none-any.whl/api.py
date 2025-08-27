from fastauth import set_auth
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .fastauth.middleware.websocket import websocket_middleware, TokenType

app = FastAPI(root_path="/test-api")
set_auth(app)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.websocket("/ws/master")
@websocket_middleware(token_type=TokenType.MASTER)
async def websocket_chat(websocket: WebSocket):
    await simple_chat(websocket=websocket)


@app.websocket("/ws/access")
@websocket_middleware(token_type=TokenType.ACCESS)
async def websocket_chat(websocket: WebSocket):
    await simple_chat(websocket=websocket)


async def simple_chat(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json(
        {
            "status": "success",
            "detail": "Connected: Connection Accepted",
        }
    )
    try:
        while True:
            query = await websocket.receive_text()
            await websocket.send_text(f"Received query: {query}")

    except WebSocketDisconnect:
        pass
