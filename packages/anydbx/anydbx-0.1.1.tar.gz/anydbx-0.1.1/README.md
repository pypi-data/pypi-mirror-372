# anydbx

Agnostic SQLAlchemy helper with engine registry, safe transactions, and pandas I/O.

```python
from pathlib import Path
from anydbx import load_config, fetch_df, write_df, execute

cfg = load_config(Path("credentials.cfg"), "wms")  # INI section

# DDL / DML
execute("CREATE TABLE t (id INT)", name="wms", cfg=cfg)

# pandas -> SQL
import pandas as pd
df = pd.DataFrame({"id": [1,2,3]})
write_df(df, "t", name="wms", cfg=cfg)

# SQL -> pandas
rows = fetch_df("SELECT * FROM t", name="wms", cfg=cfg)
