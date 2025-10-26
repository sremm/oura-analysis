import duckdb
import pandas as pd
import streamlit as st
from loguru import logger
from plotly import express as px

from oura_analysis.loader import duckdb_connect, load_base_data_into_db, load_query
from oura_analysis.settings import DATA_FOLDER

st.set_page_config(page_title="Oura Sleep Analysis", layout="wide")


def load_data_and_prepare_data(duckdb_conn: duckdb.DuckDBPyConnection) -> tuple:
    load_base_data_into_db(duckdb_conn)

    # Create a combined analyis table
    # join the tables on sleep_score.previous_day and tags.start_day
    analysis_query = load_query("oura_analysis/caffeine_analysis_query.sql")
    duckdb_conn.execute(analysis_query)


def main():
    duckdb_conn = duckdb_connect()
    load_data_and_prepare_data(duckdb_conn)

    analysis_table = duckdb_conn.execute("SELECT * FROM analysis_table").fetch_df()
    st.write("### Sample rows from analysis_table")
    st.write(f"Total rows in analysis_table: {len(analysis_table)}")
    st.dataframe(analysis_table)

    ## PLOTTING
    # Now lets also create some plots
    fig = px.histogram(
        analysis_table,
        x="sleep_score",
        color="caffeine_timing",
        title="Sleep Score by Previous Day Caffeine",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Daily chart showing sleep score, and scatter plot point colored by caffeine timing
    daily_fig = px.scatter(
        analysis_table,
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

    st.write("### Caffeine timing by hour of day")

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
