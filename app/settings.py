import os
from dotenv import load_dotenv

load_dotenv()


# databases
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tinymail.db")
# https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

REDISCLOUD_URL = os.getenv("REDISCLOUD_URL", "redis://localhost:6379/0")

CONF_TOKEN_SECRET_KEY = os.getenv("CONF_TOKEN_SECRET_KEY")
CONF_TOKEN_PASSWORD_SALT = os.getenv("CONF_TOKEN_PASSWORD_SALT")

MAIL_ADDRESS = "louis@mokomo.email"
MAIL_PWD = "txqasqvtigaourxc"

BASE_URL = "http://127.0.0.1:8000"
UNSUBSCRIBE_URL = BASE_URL + "/api/webhooks/unsubscribe"
PIXEL_URL = BASE_URL + "/api/webhooks/pixel"
