# tinymail
 A tiny bulk email software


## Start

Run the following commands to start:
- a redis instance
- a celery worker instance
- the main web app

```shell
redis-server # start a redis instance
celery -A app.worker worker -l info # start 
uvicorn app.main:app
```


## Alembic

```shell
alembic init migrations
alembic revision --autogenerate -m "your message"
alembic upgrade head
```

