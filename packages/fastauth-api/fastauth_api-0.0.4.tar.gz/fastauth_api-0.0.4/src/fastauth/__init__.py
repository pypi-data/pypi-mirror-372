"""
Fastauth — Token-based authentication for FastAPI.
### Features
- `Fastauth`: adds middleware, token routes, and OpenAPI schema.
- `TokenRouter`: endpoints for generating/refreshing tokens.
- `AccessTokenMiddleware`: validates ACCESS-TOKEN and MASTER-TOKEN.
- `websocket_middleware` / `TokenType`: WebSocket protection.

[documentation](https://github.com/rb58853/fastauth-api)
"""

from .routers.auth import TokenRouter
from .app import Fastauth, FastauthSettings
from .openapi.openapi import FastauthOpenAPI
from .middleware import AccessTokenMiddleware, websocket_middleware, TokenType


__all__ = [
    "Fastauth",
    "TokenRouter",
    "AccessTokenMiddleware",
    "FastauthOpenAPI",
    "websocket_middleware",
    "TokenType",
    "FastauthSettings",
]
