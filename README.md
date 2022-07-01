# tinymail

For something in between [Mailchimp](https://mailchimp.com) and [Mailgun](https://www.mailgun.com/), but free.

This is a simple API based on [FastAPI](https://github.com/tiangolo/fastapi), [SQLModel](https://github.com/tiangolo/sqlmodel) and [Celery](https://github.com/celery/celery)


## What can you do with it ?

- [X] Import contacts with as many metadata as you want and filter automatically the wrong emails
- [X] Create marketing campaigns and filter contacts into segments
- [X] Get access to your campaigns's open rates
- [X] Send unique emails right now or at a specific date


## How ?

### Installation

```shell
git clone https://github.com/lmanhes/tinymail
pip install -r requirements.txt
```


### Settings

Create a .env file (or create env var) with the following variables:

```
# Your EMAIL + SMTP config
MAIL_ADDRESS = "hello.tinymail.com"
MAIL_PWD = "tinymailpassword"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = "465"
SMTP_SSL = "True"

CONF_TOKEN_SECRET_KEY # random string, useful for encryption of tokens inside mails
CONF_TOKEN_PASSWORD_SALT # random string, useful for encryption of tokens inside mails

DATABASE_URL
REDISCLOUD_URL 
BASE_URL = "https://myapi/" # this is the API base url

ENV_STATE # dev/staging/prod/...
```


### Usage

Run the following commands to start:
- a redis instance
- a celery worker instance
- the main web app

```shell
redis-server
celery -A app.worker worker -l info
uvicorn app.main:app
```


## Alembic migrations

```shell
alembic revision --autogenerate -m "your message"
alembic upgrade head
```
