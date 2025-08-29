from __future__ import annotations
from typing import Optional, Any, Dict
import pandas as pd
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy import text
from .config import DbConfig
from .manager import connect, transaction

def fetch_df(sql: str, *, name: str, cfg: DbConfig, params: Optional[Dict[str, Any]] = None, index_col: Optional[str] = None) -> pd.DataFrame:
    """
    Read a query into a pandas DataFrame with a managed connection.
    Retries once on PendingRollbackError (common in reused connections).
    """
    try:
        with connect(name, cfg) as conn:
            return pd.read_sql(sql, con=conn, params=params, index_col=index_col)
    except PendingRollbackError:
        with connect(name, cfg) as conn:
            return pd.read_sql(sql, con=conn, params=params, index_col=index_col)

def write_df(df: pd.DataFrame, table: str, *, name: str, cfg: DbConfig, if_exists: str = "append", index: bool = False) -> None:
    """
    Write a DataFrame via to_sql inside an explicit transaction.
    """
    with transaction(name, cfg) as conn:
        df.to_sql(table, con=conn, if_exists=if_exists, index=index)
