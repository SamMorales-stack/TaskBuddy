from __future__ import annotations

import os
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///taskbuddy.db")

_connect_args = {"check_same_thread": False} if _DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(_DATABASE_URL, connect_args=_connect_args)

if _DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _fk_pragma(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@contextmanager
def session_scope():
    s = SessionLocal()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


def init_db() -> None:
    from taskbuddy.models import Base
    Base.metadata.create_all(engine)
