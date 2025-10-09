"""Reusable metric display components."""

import streamlit as st
import pandas as pd


def display_summary_metrics(df: pd.DataFrame, fetch_time: str):
    """Display summary metrics at the top of the page."""
    total_players = len(df)
    avg_age = df["Age"].mean()
    players_with_org_rank = df["Org Rank"].notna().sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Players", total_players)
    with col2:
        st.metric("Average Age", f"{avg_age:.1f}" if pd.notna(avg_age) else "N/A")
    with col3:
        st.metric("Ranked Prospects", players_with_org_rank)

    if fetch_time:
        st.caption(f"📅 Data fetched: {fetch_time}")


def display_analytics(df: pd.DataFrame, hitters_df: pd.DataFrame = None, pitchers_df: pd.DataFrame = None):
    """Display analytics and insights section."""
    st.subheader("Analytics & Insights")

    # Additional insights
    st.write("**Key Insights:**")
    col1, col2 = st.columns(2)
    with col1:
        young_prospects = len(df[df["Age"] <= 23])
        st.metric("Young Prospects (≤23)", young_prospects)
    with col2:
        ranked_prospects = len(df[df["Org Rank"] <= 20])
        st.metric("Top-20 Org Prospects", ranked_prospects)

    # Team with most exposure
    team_counts = df["Current Org"].value_counts()
    most_exposed_team = team_counts.idxmax()
    most_exposed_count = team_counts.max()

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Players by Organization**")
        st.caption(f"Most exposed: {most_exposed_team} ({most_exposed_count} players)")
        st.bar_chart(team_counts.sort_values(ascending=True))

    with col2:
        st.write("**Players by Position**")
        position_counts = df["Position"].value_counts()
        st.caption(f"Most common: {position_counts.idxmax()} ({position_counts.max()} players)")
        st.bar_chart(position_counts.sort_values(ascending=True))

    # Add level breakdown if stats are available
    if hitters_df is not None or pitchers_df is not None:
        st.write("")  # Spacing
        display_level_breakdown(hitters_df, pitchers_df)


def display_level_breakdown(batting_df: pd.DataFrame, pitching_df: pd.DataFrame):
    """Display a breakdown of players by level."""

    st.write("**Players by Level**")

    col1, col2 = st.columns(2)

    with col1:
        if batting_df is not None and not batting_df.empty and 'aLevel' in batting_df.columns:
            st.write("Hitters")
            level_counts = batting_df['aLevel'].value_counts()
            st.bar_chart(level_counts)
        else:
            st.write("Hitters: No data")

    with col2:
        if pitching_df is not None and not pitching_df.empty and 'aLevel' in pitching_df.columns:
            st.write("Pitchers")
            level_counts = pitching_df['aLevel'].value_counts()
            st.bar_chart(level_counts)
        else:
            st.write("Pitchers: No data")