from pathlib import Path

import duckdb

from oura_analysis.loader import duckdb_connect
from oura_analysis.settings import DATA_FOLDER

duckdb_conn = duckdb_connect(new_file=False)

query = """
SELECT *,
    start_time::TIMESTAMPTZ AS tag_start_time_tz,
    start_time::TIMESTAMP AS tag_start_time_no_tz
FROM tags"""
data = duckdb_conn.execute(query).fetch_df()
folder = Path(DATA_FOLDER) / "tmp"
folder.mkdir(exist_ok=True)
data.to_csv(folder / "tags_data_sample.csv", index=False)
