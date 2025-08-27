import logging
import os
from contextlib import contextmanager
from typing import Dict, Any, Generator

from sqlalchemy import (
    DateTime,
    Integer,
    Column,
    inspect,
    func,
    orm,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

# ——— Function to get the database URL dynamically ———
def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logging.warning("No DATABASE_URL provided; falling back to sqlite file.")
        database_url = "sqlite:///./config.db"
    return database_url

# ——— Module-level Engine & SessionLocal ———
DATABASE_URL = get_database_url()
_engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_size=100,         # sensible default; tweak to your needs
    max_overflow=0,       # avoid exceeding pool_size
    pool_pre_ping=True,   # recycle stale connections
    # echo_pool="debug",  # uncomment if you need pool debug logging
)

def get_engine():
    return _engine

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=_engine,
)

class Base(DeclarativeBase):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def _repr(self, **fields: Dict[str, Any]) -> str:
        field_strings = []
        attached = False
        for key, val in fields.items():
            try:
                field_strings.append(f"{key}={val!r}")
                attached = True
            except orm.exc.DetachedInstanceError:
                field_strings.append(f"{key}=DetachedInstanceError")
        if attached:
            return f"<{self.__class__.__name__}({', '.join(field_strings)})>"
        return f"<{self.__class__.__name__} at {hex(id(self))}>"

@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope around a series of operations.
    Commits on success, rolls back on exception, and always closes.
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_table_if_not_exist(model) -> (bool, bool):
    """
    Ensure the table for `model` exists.
    Returns (already_exists, just_created).
    """
    inspector = inspect(_engine)
    already, created = inspector.has_table(model.__tablename__), False
    if not already:
        model.__table__.create(bind=_engine)
        logging.info(f"Created table '{model.__tablename__}'")
        created = True
    else:
        logging.info(f"Table '{model.__tablename__}' already exists")
    return already, created
