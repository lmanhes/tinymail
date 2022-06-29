from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):

    ENV_STATE: str

    MAIL_ADDRESS: str
    MAIL_PWD: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_SSL: bool

    CONF_TOKEN_SECRET_KEY: str
    CONF_TOKEN_PASSWORD_SALT: str

    DATABASE_URL: str
    REDISCLOUD_URL: str
    BASE_URL: str
    UNSUBSCRIBE_URL: Optional[str] = None
    PIXEL_URL: Optional[str] = None

    class Config:
        """Loads the dotenv file."""
        env_file: str = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)

        self.UNSUBSCRIBE_URL = self.BASE_URL + "/api/webhooks/unsubscribe"
        self.PIXEL_URL = self.BASE_URL + "/api/webhooks/pixel"


settings = Settings()
