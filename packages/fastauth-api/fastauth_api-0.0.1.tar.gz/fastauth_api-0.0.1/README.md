# Fastauth-api

<div align = center>

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/pypi/v/fastauth-api?color=%2334D058&label=Version)](https://pypi.org/project/fastauth-api)
[![Stars](https://img.shields.io/github/stars/rb58853/fastauth-api?style=flat&logo=github)](https://github.com/rb58853/fastauth-api/stargazers)
[![Forks](https://img.shields.io/github/forks/rb58853/fastauth-api?style=flat&logo=github)](https://github.com/rb58853/fastauth-api/network/members)
[![Contributors](https://img.shields.io/github/contributors/rb58853/fastauth-api)](https://github.com/rb58853/fastauth-api/graphs/contributors)
[![Commit activity](https://img.shields.io/github/commit-activity/m/rb58853/fastauth-api)](https://github.com/rb58853/fastauth-api/commits)
[![Last commit](https://img.shields.io/github/last-commit/rb58853/fastauth-api.svg?style=flat)](https://github.com/rb58853/fastauth-api/commits)
[![MSeeP](https://img.shields.io/badge/Fastapi-Middelware-009688)](https://fastapi.tiangolo.com/tutorial/middleware/)


<!-- [![Watchers](https://img.shields.io/github/watchers/rb58853/fastauth-api?style=flat&logo=github)](https://github.com/rb58853/fastauth-api) -->
<!-- [![PyPI Downloads](https://static.pepy.tech/badge/fastauth-api)](https://pepy.tech/projects/fastauth-api) -->

</div>

Fastauth-api is an authentication middleware designed to integrate with `FastAPI` applications. It provides generation and management of access and refresh tokens, as well as utilities for encryption and secure key management. It is intended to simplify implementing token-based authentication policies and storing tokens in a generic backend exposed via a REST API.

Summary of main features:

- Generation of Access Tokens and Refresh Tokens.
- Integration with an external API for token persistence.
- Support for a "master token" that enables privileged operations.
- Utilities to generate and store secure encryption keys.
- Configurable middleware to protect routes by levels (master / access).

## Installation

Install from PyPI:

```bash
pip install fasauth-api
```

## Configuration file

Create in the project root a file named `fastauth.config.json` with the minimal structure:

```json
{
    "app-name": "fastauth",
    "database-api-url": "http://127.0.0.1:8000/mydb/data",
    "master-token": "<your-master-token>",
    "cryptography-key": "<your-32-byte-cryptography-key>",
    "headers": {
        "custom-header": "value",
        "...": "..."
    },
    "master-token-paths": [
        "list of your root endpoints that need master token for use"
    ],
    "access-token-paths": [
        "list of your root endpoints that need access token for use"
    ]
}
```

In this configuration:

- `app-name`: identifier name of the application.
- `database-api-url`: endpoint of the API responsible for persisting tokens.
- `master-token`: (optional) token with privileges for administrative operations.
- `cryptography-key`: (optional) key used to encrypt/decrypt payloads.
- `master-token-paths` and `access-token-paths`: route patterns that require validation by token type.

If you don't include `master-token` or `cryptography-key` in the file, you can define them via environment variables (see next section).

See example: [`fastauth.config.json`](./examples/apps/basic_api/fastauth.config.json)

### Environment variables (alternative)

You can define sensitive keys in your `.env`:

```.env
CRYPTOGRAPHY_KEY=kAONxbkATfyk3kmnUhw7YyAMotmvuJ6tVsuT1w3A6N4=
MASTER_TOKEN=kAONxbkATfyk3kmnUhw7YyAMotmvuJ6tVsuT1w3A6N4=
```

When both sources (config file and environment variables) are available, the value in the config file has priority.

## Key and token generation (utilities)

Fastauth includes utilities to generate secure keys and write variables to the environment:

- Generate a CRYPTOGRAPHY_KEY:

```python
from fastauth.utils import generate_cryptography_key
generate_cryptography_key()
```

- Generate and write a MASTER_TOKEN to the environment file:

```python
from cryptography.fernet import Fernet
from fastauth.utils import writekey2env

key = Fernet.generate_key().decode()
writekey2env(key=key, name="MASTER_TOKEN")
```

These utilities allow creating secure keys compatible with the internal encryption system.

## Basic usage (FastAPI integration)

Minimal integration example:

```python
from fastapi import FastAPI
from fastauth import set_auth

app = FastAPI(root_path="/test-api")
set_auth(app)

@app.get("/health")
async def health_check():
        return {"status": "healthy"}

@app.get("/access/health")
async def access_health_check():
        return {"service": "access health that need access token", "status": "healthy"}

@app.get("/master/health")
async def master_health_check():
        return {"service": "master health that need master token", "status": "healthy"}
```

`set_auth(app)` applies the middleware and the routers required for issuing and verifying tokens according to the configuration.

[see more examples](./examples/EXAMPLES.md)

## Using the /auth/token router

The package exposes a router with two public endpoints for generating and renewing JWT tokens. These endpoints are registered under the configured prefix (default `/auth`) and return a standardized response with status, message, HTTP code and a `data` block containing the tokens and the `client_id`.

### Main endpoints

- **`GET /auth/token/new`**
  - Description: Generates a new pair of tokens (access + refresh). If `client_id` is provided, the tokens are associated with that identifier; otherwise, a random `client_id` is generated.
  - Query params:
    - client_id (optional): string
  - Response (200 OK, example):

    ```json
        {
            "status": "success",
            "message": "Token generated",
            "code": 200,
            "data": {
                "client_id": "abc-123",
                "access_token": "<jwt_access_token>",
                "refresh_token": "<jwt_refresh_token>"
            }
        }
    ```

  - Common errors:
    - 500 INTERNAL SERVER ERROR: if the encryption key (`CRYPTOGRAPHY_KEY`) is not configured.
- **`GET /auth/token/refresh`**
  - Description: Validates a `refresh_token` and issues a new pair of tokens associated with the `client_id` contained in the refresh token.
  - Query params:
    - refresh_token (required): string
  - Behavior:
    - Decodes the refresh token with the encryption key using HS256.
    - If the token is valid and contains `client_id`, new tokens are generated.
  - Responses:
    - Success: same structure as `/token/new`.
    - 401 UNAUTHORIZED: invalid token or missing `client_id`.
    - 500 INTERNAL SERVER ERROR: if the encryption key is missing.

### Configuration requirements

- `CRYPTOGRAPHY_KEY`: secret key used to sign and verify JWTs. Must be present in the configuration file (`fastauth.config.json`) or in environment variables (file value takes precedence). Without this key, the endpoints will return errors and be unusable.
- `database-api-url`: the implementation internally calls `save_token(...)` to persist tokens; ensure that the persistence API is available and correctly configured.

### Relevant technical details

- JWT algorithm: HS256.
- Default durations:
  - Access token: 30 days
  - Refresh token: 365 days
- Payloads: include `client_id`, `type` (`access` or `refresh`), `iat` and `exp`.
- Persistence: when generating tokens, the `save_token` function saves the `client_id`, `access_token` and `refresh_token` in the configured backend.

### Usage examples

- Curl: generate new token (without client_id):

    ```bash
    curl -X GET "http://localhost:8000/auth/token/new"
    ```

- Curl: generate new token (with client_id):

    ```bash
    curl -X GET "http://localhost:8000/auth/token/new?client_id=my-client-id"
    ```

- Curl: refresh using refresh token:

    ```bash
    curl -G "http://localhost:8000/auth/token/refresh" --data-urlencode "refresh_token=<jwt_refresh_token>"
    ```

- Python (requests) — generate:

    ```python
    import requests
    r = requests.get("http://localhost:8000/auth/token/new", params={"client_id":"my-client"})
    print(r.json())
    ```

### Customization

- For custom logic you can extend TokenRouter and override the private methods exposed in the class (for example `__generate_access_token` and `__refresh_access_token`) and then include the router with:

    ```python
    token_router = TokenRouter() # or a custom subclass
    app.include_router(token_router.route)
    ```

### Errors and representative messages

- `"Crypto key not set"` → missing CRYPTOGRAPHY_KEY (500)
- `"Invalid refresh token"` → token not decodable or corrupted (401)
- `"Invalid refresh token: missing client_id"` → valid refresh token but without client_id (401)

## TODO / Roadmap

- Expand compatibility with different encrypted payload formats.
- Restructure and scale the websocket decorator implementation.
- Fully document each endpoint so that it appears in Swagger/OpenAPI.
- Rotate the key carefully: implement migration if the encryption key changes, since tokens signed with the previous key will become invalid.
- Use the access token as a Bearer in the Authorization header to protect routes that require validation:
    Authorization: Bearer <access_token>

## Version status

- **🔐 Token-based authentication system (Access + Refresh) with endpoints ready:** check the `/auth` router and the `/token/new` and `/token/refresh` endpoints in [auth.py](src/fastauth/routers/auth.py).
- **⚙️ Easy integration with `FastAPI`:** function [`set_auth(app)`](src/fastauth/quick_app.py) applies middleware, registers routes and replaces the OpenAPI with FastauthOpenAPI.
- **🛡 Configurable middleware:** Master / Access level protection based on routes defined in the configuration. Supports validation of MASTER-TOKEN and ACCESS-TOKEN headers.
- **🧾 Flexible configuration:** values from `fastauth.config.json` or environment variables (`.env`).
- **🔑 Basic key management and utilities:**
  - Generate `CRYPTOGRAPHY_KEY` with `generate_cryptography_key()`.
  - Read/write variables in `.env` using `writekey2env(...)`.
- 🧠 JWT tokens signed with HS256 and payloads containing `client_id`, `type`, `iat`, `exp`.
- **💾 Decoupled token persistence:** `save_token` / `load_access_token` interact with an external API configurable via `"database-api-path"` in the configuration file.
- **🔌 WebSocket support:** authentication decorator for websockets (checks ACCESS-TOKEN in headers).
- **🧰 Extensible:** `TokenRouter` can be extended to customize token generation/renewal; middleware and OpenAPI are easily replaceable/adjustable.

[see full version history](./doc/CHANGELOG.md)

## License

Project under the MIT license. See the LICENSE file for details.

---
<div align = center>

#### If you find this project helpful, please don’t forget to ⭐ star the [repository](https://github.com/rb58853/fastauth-api)

</div>
