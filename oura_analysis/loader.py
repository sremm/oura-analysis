from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
from loguru import logger

from oura_analysis.settings import DATA_FOLDER, REPO_ROOT


class OuraData:
    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data

    @property
    def data_table(self) -> pd.DataFrame:
        """Fetches data in a pandas DataFrame"""
        return self._data.copy()

    @staticmethod
    def from_path(path: Path) -> OuraData:
        """Loads data from a path"""
        return OuraData(pd.read_csv(path, sep=";", header=0))


def load_query(name: str) -> str:
    query_file = REPO_ROOT / name
    with open(query_file, "r") as f:
        return f.read()


def duckdb_connect() -> duckdb.DuckDBPyConnection:
    db_filename = DATA_FOLDER / "sleep_analysis_2020-05-01_2026-01-01.duckdb"

    # as of now recreated each time when script is run
    if db_filename.exists():
        db_filename.unlink()

    duckdb_conn = duckdb.connect(database=db_filename)
    return duckdb_conn


def load_base_data_into_db(duckdb_conn: duckdb.DuckDBPyConnection) -> tuple:
    ## DATA LOADING
    sleep_score_file = DATA_FOLDER / "sleep_score_data_2020-05-01_2026-01-01.json"
    sleep_data_file = DATA_FOLDER / "sleep_data_2020-05-01_2026-01-01.json"
    tags_file = DATA_FOLDER / "tags_data_2020-05-01_2026-01-01.json"

    logger.info("Loading sleep data")
    sleep_score_data = duckdb_conn.read_json(sleep_score_file)
    sleep_data = duckdb_conn.read_json(sleep_data_file)
    tags_data = duckdb_conn.read_json(tags_file)

    ## DATA PREPARATION
    logger.info("Creating tables in DuckDB")
    duckdb_conn.execute(
        "CREATE OR REPLACE TABLE sleep_score AS SELECT * FROM sleep_score_data"
    )
    duckdb_conn.execute("CREATE OR REPLACE TABLE sleep AS SELECT * FROM sleep_data")
    duckdb_conn.execute("CREATE OR REPLACE TABLE tags AS SELECT * FROM tags_data")

    logger.info("Inspecting tables")
    logger.info(
        f"Sleep table columns: {duckdb_conn.execute('DESCRIBE sleep_score').fetchall()}"
    )
    logger.info(
        f"Tags table columns: {duckdb_conn.execute('DESCRIBE tags').fetchall()}"
    )

    # Add previous day to sleep table
    logger.info("Adding previous_day column to sleep_score table")
    duckdb_conn.execute("ALTER TABLE sleep_score ADD COLUMN previous_day DATE")
    duckdb_conn.execute("UPDATE sleep_score SET previous_day = day - 1")
