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
        logger.error(
            "Configuration file not found. Please create .fastauth.config.json."
        )

config: dict = ConfigFile.DATA


class ConfigServer:
    MASTER_TOKEN: str | None = (
        config.get("master-token", None)
        if config.get("master-token", None) is not None
        else os.getenv("MASTER_TOKEN", None)
    )

    MASTER_PATHS: list[str] = ["/auth/token/new"] + config.get("master-token-paths", [])
    ACCESS_TOKEN_PATHS: list[str] = config.get("access-token-paths", [])


class TokenConfig:
    CRYPTOGRAPHY_KEY: str = os.getenv("CRYPTOGRAPHY_KEY", None) or config.get(
        "cryptography-key", None
    )


class DatabaseConfig:
    PATH: str | None = (
        config.get("database-api-path", None)
        if config.get("database-api-path", None) is not None
        else None
    )
