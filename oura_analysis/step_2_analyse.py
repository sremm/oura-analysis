import duckdb
import pandas as pd
import streamlit as st
from loguru import logger
from plotly import express as px

from oura_analysis.settings import DATA_FOLDER, REPO_ROOT

st.set_page_config(page_title="Oura Sleep Analysis", layout="wide")


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


def load_data(duckdb_conn: duckdb.DuckDBPyConnection) -> tuple:
    ## DATA LOADING
    sleep_score_file = DATA_FOLDER / "sleep_score_data_2020-05-01_2026-01-01.json"
    sleep_data_file = DATA_FOLDER / "sleep_data_2020-05-01_2026-01-01.json"
    tags_file = DATA_FOLDER / "tags_data_2020-05-01_2026-01-01.json"

    logger.info("Loading sleep data")
    sleep_score_data = duckdb_conn.read_json(sleep_score_file)
    sleep_data = duckdb_conn.read_json(sleep_data_file)
    tags_data = duckdb_conn.read_json(tags_file)
    return sleep_score_data, sleep_data, tags_data


def main():
    duckdb_conn = duckdb_connect()
    sleep_score_data, sleep_data, tags_data = load_data(duckdb_conn)

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

    # Create a combined analyis table
    # join the tables on sleep_score.previous_day and tags.start_day
    analysis_query = load_query("oura_analysis/analysis_query.sql")
    duckdb_conn.execute(analysis_query)
    combined_query_result = duckdb_conn.execute(
        "SELECT * FROM analysis_table"
    ).fetch_df()

    st.write("### Sample rows from analysis_table")
    st.write(f"Total rows in analysis_table: {len(combined_query_result)}")
    st.dataframe(combined_query_result)

    ## PLOTTING
    # Now lets also create some plots
    fig = px.histogram(
        combined_query_result,
        x="sleep_score",
        color="caffeine_timing",
        title="Sleep Score by Previous Day Caffeine",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Daily chart showing sleep score, and scatter plot point colored by caffeine timing
    daily_fig = px.scatter(
        combined_query_result,
        x="sleep_date",
        y="sleep_score",
        color="caffeine_timing",
        title="Daily Sleep Score",
    )
    st.plotly_chart(daily_fig, use_container_width=True)

    # Create a grouped stats table with each row showing sleep score stats based on previous day caffeine count
    grouped_stats = duckdb_conn.execute(
        """
        SELECT
            previous_day_caffeine_count,
            MIN(sleep_score) AS min,
            MAX(sleep_score) AS max,
            AVG(sleep_score) AS mean,
            MEDIAN(sleep_score) AS median,
            COUNT(*) AS count
        FROM analysis_table
        GROUP BY previous_day_caffeine_count
        ORDER BY previous_day_caffeine_count
        """
    ).fetch_df()

    # Add a row for coffee count > 1
    more_than_one_stats = duckdb_conn.execute(
        """
        SELECT
            '>0' AS previous_day_caffeine_count,
            MIN(sleep_score) AS min,
            MAX(sleep_score) AS max,
            AVG(sleep_score) AS mean,
            MEDIAN(sleep_score) AS median,
            COUNT(*) AS count
        FROM analysis_table
        WHERE previous_day_caffeine_count > 0
        """
    ).fetch_df()
    st.write("### Grouped Sleep Score Stats by Previous Day Caffeine Count")
    grouped_stats = pd.concat([grouped_stats, more_than_one_stats], ignore_index=True)
    st.dataframe(grouped_stats)

    st.write("### Caffeine timing vs Sleep Score")

    caffeine_timing = duckdb_conn.execute(
        """
        SELECT
            COUNT(*) AS caffeine_count,
            EXTRACT(
                'hour'
                from start_time::timestamp
            ) AS caffeine_hour
        FROM tags
        WHERE comment = 'Coffee'
            OR tag_type_code IN ('tag_generic_coffee', 'tag_generic_caffeine')
            OR (
                tag_type_code = 'custom'
                AND custom_name = 'Mate'
            )
        GROUP BY caffeine_hour
        ORDER BY caffeine_hour
        """
    )
    caffeine_timing_df = caffeine_timing.fetch_df()
    # st.dataframe(caffeine_timing_df)
    # Add bar chart showing caffeine counts by hour
    # y axis is count of caffeine events
    # x axis is hour of day
    caffeine_timing_fig = px.bar(
        caffeine_timing_df,
        x="caffeine_hour",
        y="caffeine_count",
        title="Caffeine Events by Hour of Day",
    )
    st.plotly_chart(caffeine_timing_fig, use_container_width=True)
    duckdb_conn.close()


if __name__ == "__main__":
    main()
