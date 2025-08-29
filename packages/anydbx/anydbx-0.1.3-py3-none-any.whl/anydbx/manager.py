from __future__ import annotations
from typing import Dict, Optional, Iterator, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.pool import NullPool
from .config import DbConfig

class EngineRegistry:
    """
    Caches SQLAlchemy Engines by logical name.
    Keeps connections short-lived via context managers.
    """
    def __init__(self) -> None:
        self._engines: Dict[str, Engine] = {}

    def get_or_create(self, name: str, cfg: DbConfig, *, stream_results: bool = True) -> Engine:
        if name in self._engines:
            return self._engines[name]

        url = cfg.to_sqla_url()
        kwargs: Dict[str, Any] = {}

        # DuckDB is file/embedded: NullPool avoids concurrency footguns.
        if cfg.type.lower() == "duckdb":
            kwargs["poolclass"] = NullPool

        engine = create_engine(url, execution_options={"stream_results": stream_results}, **kwargs)
        self._engines[name] = engine
        return engine

    def dispose(self, name: Optional[str] = None) -> None:
        if name is None:
            for e in self._engines.values():
                e.dispose()
            self._engines.clear()
            return
        eng = self._engines.pop(name, None)
        if eng:
            eng.dispose()

registry = EngineRegistry()

@contextmanager
def connect(name: str, cfg: DbConfig) -> Iterator[Connection]:
    """
    Yields a live Connection; closes it afterwards.
    Typical usage:
        with connect("wms", cfg) as conn:
            conn.execute(text("SELECT 1"))
    """
    eng = registry.get_or_create(name, cfg)
    conn = eng.connect()
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def transaction(name: str, cfg: DbConfig) -> Iterator[Connection]:
    """
    Transactional context manager with commit/rollback.
    """
    with connect(name, cfg) as conn:
        trans = conn.begin()
        try:
            yield conn
            trans.commit()
        except Exception:
            trans.rollback()
            raise

def execute(sql: str, params: Optional[dict] = None, *, name: str, cfg: DbConfig) -> None:
    """Execute a statement inside its own transaction (autocommit semantics)."""
    with transaction(name, cfg) as conn:
        conn.execute(text(sql), params or {})

def dispose_all() -> None:
    """Dispose every cached engine."""
    registry.dispose()
