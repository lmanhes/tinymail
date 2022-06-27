from sqlmodel import create_engine, Session

from app import settings


engine = create_engine(settings.DATABASE_URL)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
