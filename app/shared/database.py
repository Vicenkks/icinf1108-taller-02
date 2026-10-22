import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://Estudiantes:postgres@localhost:5432/estudiantes",
)

engine = create_engine(DATABASE_URL, echo=True, future=True)

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def get_db()-> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()