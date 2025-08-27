from ..config import TokenConfig, logger
from jose import jwt

ALGORITHM = "HS256"


class TokenCriptografy:
    def decode(token):
        if not TokenConfig.CRYPTOGRAPHY_KEY:
            logger.error(
                "CRYPTOGRAFY_KEY is not set. Please set it in the environment or config file."
            )
            raise Exception(
                "Internal Server Error: CRYPTOGRAFY_KEY is not set"
            )
        return jwt.decode(
            token,
            TokenConfig.CRYPTOGRAPHY_KEY,
            algorithms=[ALGORITHM],
        )

    def encode(payload):
        return jwt.encode(
            payload,
            TokenConfig.CRYPTOGRAPHY_KEY,
            algorithm=ALGORITHM,
        )
