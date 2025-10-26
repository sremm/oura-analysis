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
    analysis_query = load_query("oura_analysis/alcohol_analysis_query.sql")
    duckdb_conn.execute(analysis_query)


def main():
    duckdb_conn = duckdb_connect()
    load_data_and_prepare_data(duckdb_conn)

    analysis_table = duckdb_conn.execute(
        "SELECT * FROM analysis_table where len(alcohol_hours) > 0"
    ).fetch_df()
    st.write("### Sample rows from analysis_table, where alcohol was consumed")
    st.write(f"Total rows in analysis_table: {len(analysis_table)}")
    st.dataframe(analysis_table)

    # ## PLOTTING
    # Now lets also create some plots
    fig = px.scatter(
        analysis_table,
        x="previous_day_alcohol_count",
        y="sleep_score",
        title="Sleep Score vs Previous Day Alcohol Count",
        color="last_alcohol_hour",
        color_continuous_scale=px.colors.sequential.Turbo,
        hover_data=["sleep_date", "alcohol_hours"],
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.scatter(
        analysis_table,
        x="last_alcohol_hour",
        y="sleep_score",
        color="previous_day_alcohol_count",
        color_continuous_scale=px.colors.sequential.Turbo,
        title="Sleep Score vs Last Alcohol Hour",
        hover_data=["sleep_date", "alcohol_hours"],
    )
    st.plotly_chart(fig, use_container_width=True)

    # Daily chart showing sleep score, and scatter plot point colored by alcohol timing
    daily_fig = px.scatter(
        analysis_table,
        x="sleep_date",
        y="sleep_score",
        color="previous_day_alcohol_count",
        color_continuous_scale=px.colors.sequential.Turbo,
        title="Daily Sleep Score",
    )
    st.plotly_chart(daily_fig, use_container_width=True)

    st.write("### Alcohol timing by hour of day")

    alcohol_timing = duckdb_conn.execute(
        """
        SELECT
            COUNT(*) AS alcohol_count,
            EXTRACT(
                'hour'
                from start_time::timestamp
            ) AS alcohol_hour
        FROM tags
        WHERE tag_type_code IN (
                'tag_sleep_alcohol',
                'tag_generic_wine',
                'tag_generic_beer'
            )
        GROUP BY alcohol_hour
        ORDER BY alcohol_hour
        """
    )
    alcohol_timing_df = alcohol_timing.fetch_df()
    # st.dataframe(alcohol_timing_df)
    alcohol_timing_fig = px.bar(
        alcohol_timing_df,
        x="alcohol_hour",
        y="alcohol_count",
        title="Alcohol Events by Hour of Day",
    )
    st.plotly_chart(alcohol_timing_fig, use_container_width=True)
    duckdb_conn.close()


if __name__ == "__main__":
    main()
