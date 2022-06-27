from itsdangerous import URLSafeTimedSerializer
from loguru import logger

from app import settings


def generate_confirmation_token(id_to_encode: str) -> str:
    serializer = URLSafeTimedSerializer(settings.CONF_TOKEN_SECRET_KEY)
    return serializer.dumps(id_to_encode, salt=settings.CONF_TOKEN_PASSWORD_SALT)


def confirm_token(token: str) -> str:
    serializer = URLSafeTimedSerializer(settings.CONF_TOKEN_SECRET_KEY)
    try:
        decoded_id = serializer.loads(token, salt=settings.CONF_TOKEN_PASSWORD_SALT)
    except:
        logger.info("token is not valid")
        return False

    return decoded_id
