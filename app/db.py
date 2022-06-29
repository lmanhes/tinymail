from sqlmodel import create_engine, Session

from settings import settings


engine = create_engine(settings.DATABASE_URL)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
