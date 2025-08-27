"""
Fastauth — Token-based authentication for FastAPI.
### Features
- `set_auth`: adds middleware, token routes, and OpenAPI schema.
- `TokenRouter`: endpoints for generating/refreshing tokens.
- `AccessTokenMiddleware`: validates ACCESS-TOKEN and MASTER-TOKEN.
- `websocket_middleware` / `TokenType`: WebSocket protection.

[documentation](https://github.com/rb58853/fastauth-api)
"""

from .quick_app import set_auth
from .routers.auth import TokenRouter
from .openapi.openapi import FastauthOpenAPI
from .middleware import AccessTokenMiddleware, websocket_middleware, TokenType


__all__ = [
    "set_auth",
    "TokenRouter",
    "AccessTokenMiddleware",
    "FastauthOpenAPI",
    "websocket_middleware",
    "TokenType",
]
