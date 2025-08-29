import os
import json
from .logger import logger


class ConfigFile:
    PATH: str = "fastauth.config.json"
    DATA: dict = {}


if ConfigFile.DATA == {}:
    # Singleton
    try:
        with open(ConfigFile.PATH, "r") as f:
            ConfigFile.DATA = json.load(f)
    except FileNotFoundError:
        logger.warning(
            "Configuration file not found. Please create '.fastauth.config.json' or pass settings via paramaters in `Fastauth()`"
        )

config: dict = ConfigFile.DATA


class ConfigServer:
    MASTER_TOKEN: str | None = (
        config.get("master_token", None)
        if config.get("master_token", None) is not None
        else os.getenv("MASTER_TOKEN", None)
    )

    MASTER_PATHS: list[str] = ["/auth/token/new"] + config.get("master_token_paths", [])
    ACCESS_TOKEN_PATHS: list[str] = config.get("access_token_paths", [])


class TokenConfig:
    CRYPTOGRAPHY_KEY: str = os.getenv("CRYPTOGRAPHY_KEY", None) or config.get(
        "cryptography_key", None
    )


class DatabaseConfig:
    PATH: str | None = (
        config.get("database_api_path", None)
        if config.get("database_api_path", None) is not None
        else None
    )
