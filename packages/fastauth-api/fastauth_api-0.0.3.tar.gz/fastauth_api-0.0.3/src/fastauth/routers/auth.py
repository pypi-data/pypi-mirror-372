import uuid
import datetime
from jose import jwt
from http import HTTPStatus
from fastapi.routing import APIRouter
from ..config import logger, TokenConfig
from ..client_db.client_db import save_token
from ..models.responses.standart import standard_response


class TokenRouter:
    """
    TokenRouter provides a modular authentication route handler for FastAPI applications, enabling easy integration of token-based authentication endpoints.

    ## Usage
    - Instantiate TokenRouter and use its `route` property to obtain an APIRouter with pre-configured `/token/new` and `/token/refresh` endpoints.
    - Pass the resulting router to your FastAPI app using `app.include_router(token_router.route)`.
    Customization:
    - To implement custom token generation logic, subclass TokenRouter and override the `__generate_access_token` and/or `__refresh_access_token` methods.
    Properties:
    - route: Returns an APIRouter instance with authentication endpoints for access and refresh token generation.

    ## Example
    ```python
    token_router = TokenRouter()
    app.include_router(token_router.route)
    # For custom logic:
    class CustomTokenRouter(TokenRouter):
        def __generate_access_token(self, client_id: str|None):
            # Custom implementation here
            pass
    custom_router = CustomTokenRouter()
    app.include_router(custom_router.route)
    ```
    """

    def __init__(
        self,
        prefix: str = "/auth",
        tags: list[str] = ["auth"],
    ):
        self.prefix = prefix
        self.tags = tags

    @property
    def route(self) -> APIRouter:
        _route = APIRouter(prefix=self.prefix, tags=self.tags)
        self.__registry_enpoints(_route)
        return _route

    def __registry_enpoints(self, router: APIRouter):
        """
        If your need custom access token generation logic, you can overwrite the methods
        `__generate_access_token` and `__refresh_access_token` in this class.
        If you don't need custom logic, you can use the default implementation provided by `BaseTokenGeneration`.
        The default implementation uses the `BaseTokenGeneration` class to generate access and refresh tokens
        based on the `client_id` or `refresh_token` provided.
        """

        @router.get("/token/new")
        async def generate_access_token(client_id: str | None = None):
            """
            Generates and returns an access token (and refresh token) for the provided `client_id`.
            This endpoint is used to obtain a new access token (and refresh token), which can be used to authenticate and authorize subsequent requests.
            Provide a valid client ID as a query parameter to receive a token associated with that client.
            Args:
                client_id (str): The unique identifier of the client requesting the access token.
            Returns:
                dict: A dictionary containing the generated access token and refresh token into `"data"` key.
            Example:
                `GET /auth//token/new?client_id=your_client_id`
            Note:
                The access token should be included in the Authorization header for protected endpoints.
            """
            return self.__generate_access_token(client_id=client_id)

        @router.get("/token/refresh")
        async def refresh_access_token(refresh_token: str):
            """
            Generates and returns an access token (and refresh token) for the provided `refresh_token`.
            This endpoint is used to obtain a new access token (and refresh token), which can be used to authenticate and authorize subsequent requests.
            Provide a valid client ID as a query parameter to receive a token associated with that client.
            Args:
                client_id (str): The unique identifier of the client requesting the access token.
            Returns:
                dict: A dictionary containing the generated access token and refresh token into `"data"` key.
            Example:
                `GET /auth//token/refresh?refresh_token=your_refresh_token`
            Note:
                The access token should be included in the Authorization header for protected endpoints.
            """
            return self.__refresh_access_token(refresh_token=refresh_token)

    def __generate_access_token(self, client_id: str | None):
        """
        This method is intended to be overwritten by developers if custom access token generation logic is required.
        It generates and returns an access token and refresh token for the given `client_id`.
        Returns:
            dict: Dict response like
            ```
            {
                status="success",
                message="Token generated",
                code=HTTPStatus.OK,
                data={
                    "client_id": client_id
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            }
            ```
        """
        return BaseTokenGeneration.generate_access_token(client_id=client_id)

    def __refresh_access_token(self, refresh_token: str):
        """
        This method is intended to be overwritten by developers if custom access token generation logic is required.
        It generates and returns an access token and refresh token for the given `refresh_token`.
        Returns:
            dict: Dict response like
            ```
            {
                status="success",
                message="Token generated",
                code=HTTPStatus.OK,
                data={
                    "client_id": client_id
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            }
            ```
        """
        return BaseTokenGeneration.refresh_access_token(refresh_token=refresh_token)


class BaseTokenGeneration:
    def generate_access_token(client_id: str | None) -> dict:
        return BaseTokenGeneration.__generate_tokens_from_client(client_id=client_id)

    def refresh_access_token(refresh_token: str) -> dict:
        CRYPTOGRAFY_KEY = TokenConfig.CRYPTOGRAPHY_KEY
        if not CRYPTOGRAFY_KEY:
            logger.error(
                "CRYPTOGRAFY_KEY is not set. Please set it in the environment or config file."
            )
            return standard_response(
                status="error",
                message="CRYPTOGRAFY_KEY is not set",
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        ALGORITHM = "HS256"

        try:
            payload = jwt.decode(refresh_token, CRYPTOGRAFY_KEY, algorithms=[ALGORITHM])
            client_id = payload.get("client_id")
            if not client_id:
                return standard_response(
                    status="error",
                    message="Invalid refresh token: missing client_id",
                    code=HTTPStatus.UNAUTHORIZED,
                )
        except Exception as e:
            logger.error(f"Failed to decode refresh token: {e}")
            return standard_response(
                status="error",
                message="Invalid refresh token",
                code=HTTPStatus.UNAUTHORIZED,
            )

        return BaseTokenGeneration.__generate_tokens_from_client(client_id=client_id)

    def __generate_tokens_from_client(client_id: str | None) -> dict:
        # Secret key for encoding the JWTs (should be kept secure in production)
        CRYPTOGRAFY_KEY = TokenConfig.CRYPTOGRAPHY_KEY
        if not CRYPTOGRAFY_KEY:
            logger.error(
                "CRYPTOGRAFY_KEY is not set. Please set it in the environment or config file."
            )
            return standard_response(
                status="error",
                message="CRYPTOGRAFY_KEY is not set",
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        ALGORITHM = "HS256"
        client_id = client_id if client_id is not None else str(uuid.uuid4())

        # Set token expiration times
        ACCESS_TOKEN_EXPIRE_DAYS = 30
        REFRESH_TOKEN_EXPIRE_DAYS = 365

        # Generate expiration times
        now = datetime.datetime.now(datetime.timezone.utc)

        access_token_expires = now + datetime.timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        refresh_token_expires = now + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        # Payloads for tokens
        access_token_payload = {
            "client_id": client_id,
            "type": "access",
            "exp": access_token_expires,
            "iat": now,
        }
        refresh_token_payload = {
            "client_id": client_id,
            "type": "refresh",
            "exp": refresh_token_expires,
            "iat": now,
        }

        # Generate JWT tokens using jose
        access_token = jwt.encode(
            access_token_payload, CRYPTOGRAFY_KEY, algorithm=ALGORITHM
        )
        refresh_token = jwt.encode(
            refresh_token_payload, CRYPTOGRAFY_KEY, algorithm=ALGORITHM
        )

        save_token(
            client_id=client_id,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        return standard_response(
            status="success",
            message="Token generated",
            code=HTTPStatus.OK,
            data={
                "client_id": client_id,
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
        )
