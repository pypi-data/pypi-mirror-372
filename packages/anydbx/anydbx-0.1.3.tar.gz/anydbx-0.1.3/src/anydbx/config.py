from __future__ import annotations
from dataclasses import dataclass
from configparser import ConfigParser
from pathlib import Path
from typing import Optional

@dataclass(frozen=True)
class DbConfig:
    """Immutable DB config used to build SQLAlchemy URL."""
    type: str
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    server: Optional[str] = None
    port: Optional[int] = None

    def to_sqla_url(self) -> str:
        t = (self.type or "").lower()
        if t in ("postgres", "postgresql", "pg"):
            host = self.server or "127.0.0.1"
            port = f":{self.port}" if self.port else ""
            # Prefer psycopg3; fallback para psycopg2 se não estiver instalado
            driver = "psycopg"
            return f"postgresql+{driver}://{self.username}:{self.password}@{host}{port}/{self.database}"

        if t == "mysql":
            host = self.server or "127.0.0.1"
            port = f":{self.port}" if self.port else ""
            return f"mysql+pymysql://{self.username}:{self.password}@{host}{port}/{self.database}"

        if t == "mssql":
            host = self.server or "127.0.0.1"
            port = f":{self.port}" if self.port else ""
            return f"mssql+pymssql://{self.username}:{self.password}@{host}{port}/{self.database}"

        if t == "duckdb":
            db = self.database or ":memory:"
            return f"duckdb:///{db}"

        raise ValueError(f"Unsupported database type: {self.type!r}")

def load_config(ini_path: Path, section: str) -> DbConfig:
    """
    Read INI credentials (compatible with your current credentials.cfg layout).
    Later we can add an EnvConfigSource; API fica estável.
    """
    parser = ConfigParser()
    if not parser.read(ini_path):
        raise FileNotFoundError(f"Could not read credentials file: {ini_path}")
    if not parser.has_section(section):
        raise KeyError(f"Section [{section}] not found in {ini_path}")

    t = parser.get(section, "type")
    if t == "duckdb":
        return DbConfig(type=t, database=parser.get(section, "database", fallback=":memory:"))

    port = parser.get(section, "port", fallback=None)
    port_int = int(port) if port and port.isdigit() else None

    return DbConfig(
        type=t,
        username=parser.get(section, "username"),
        password=parser.get(section, "password"),
        database=parser.get(section, "database"),
        server=parser.get(section, "server"),
        port=port_int,
    )
