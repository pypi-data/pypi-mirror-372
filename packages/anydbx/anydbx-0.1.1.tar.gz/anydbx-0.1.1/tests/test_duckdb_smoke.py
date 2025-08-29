from pathlib import Path
import pandas as pd
from dataclasses import replace
from anydbx import load_config, fetch_df, write_df, execute

def test_duckdb_smoke(tmp_path: Path):
    # Load in-memory DuckDB
    dbfile = tmp_path / "test.duckdb"
    cfg = load_config(Path(__file__).with_name("sample-credentials.cfg"), "duck")
    cfg = replace(cfg, database=str(dbfile))

    # Create a table
    execute("CREATE TABLE t (id INTEGER, name TEXT)", name="duck", cfg=cfg)

    # Write some data
    df = pd.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"]})
    write_df(df, "t", name="duck", cfg=cfg, if_exists="append", index=False)

    # Read back
    out = fetch_df("SELECT count(*) AS n FROM t", name="duck", cfg=cfg)
    assert int(out.iloc[0, 0]) == 3
