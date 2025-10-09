"""Player Data page - displays Rule 5 eligible players and analytics."""

import streamlit as st
import pandas as pd

from data.fangraphs import fetch_rule5_players
from data.prospect_savant import fetch_prospect_savant_data
from data.fangraphs_minors_stats import (
    get_all_minors_stats,
    merge_rule5_with_minors_stats
)
from data.data_processing import merge_rule5_with_savant, apply_filters
from utils.constants import MIN_ORG_RANK_FOR_TOP_PROSPECTS
from components.tables import (
    display_aaa_hitters_table,
    display_aaa_pitchers_table,
    display_top_prospects_table,
    display_all_players_table,
    display_basic_batting_stats,
    display_basic_pitching_stats
)
from components.metrics import display_summary_metrics, display_analytics


def render():
    """Render the Player Data page."""
    st.caption("All players currently eligible for the Rule 5 draft per FanGraphs RosterResource")

    # Fetch button
    if st.button("Fetch Latest Eligibility", type="primary"):
        st.cache_data.clear()
        st.rerun()

    # Fetch data
    with st.spinner("Fetching player data..."):
        df, fetch_time = fetch_rule5_players()
        st.session_state.last_fetch_time = fetch_time
        savant_df = fetch_prospect_savant_data()

        # Fetch basic stats for all levels
        batting_stats_df, pitching_stats_df = get_all_minors_stats(season=2025)

    if not df.empty:
        # Display summary metrics
        display_summary_metrics(df, st.session_state.last_fetch_time)
        st.divider()

        # AAA Players with Advanced Stats (ProspectSavant)
        if not savant_df.empty:
            display_aaa_section(df, savant_df)
            st.divider()

        # Top Prospects Section
        display_top_prospects_section(df)
        st.divider()

        # Analytics Section (now includes level breakdown)
        display_analytics_section(df, batting_stats_df, pitching_stats_df)
        st.divider()

        # Filters and Main Table
        display_filters_and_table(df)

        st.divider()

        # Basic Stats Section moved to bottom
        display_basic_stats_section(df, batting_stats_df, pitching_stats_df)

    else:
        st.info("👆 Click the button above to fetch the latest Rule 5 eligible players")

    # Footer
    st.divider()
    st.caption(
        "Prospect draft info and rankings courtesy of FanGraphs | "
        "Triple A advanced metrics and prospect scores courtesy of ProspectSavant"
    )
    st.caption(
        "Rule 5 Draft Dashboard is not affiliated with MLB, nor with any of their digital properties. "
        "All rights reserved."
    )


def display_analytics_section(df: pd.DataFrame, batting_df: pd.DataFrame, pitching_df: pd.DataFrame):
    """Display analytics section with level breakdown."""
    # Merge Rule 5 eligible players with stats to get level breakdown
    hitters_merged, pitchers_merged = merge_rule5_with_minors_stats(df, batting_df, pitching_df)

    # Pass the merged dataframes to display_analytics (which now includes level breakdown)
    display_analytics(df, hitters_merged, pitchers_merged)


def display_basic_stats_section(df: pd.DataFrame, batting_df: pd.DataFrame, pitching_df: pd.DataFrame):
    """Display section with basic stats for all eligible players."""
    st.subheader("Season Stats - All Levels")
    st.caption("2025 season statistics from FanGraphs")

    if batting_df.empty and pitching_df.empty:
        st.info("Basic stats not available. Check your internet connection or try refreshing.")
        return

    # Merge Rule 5 eligible players with stats
    hitters_merged, pitchers_merged = merge_rule5_with_minors_stats(df, batting_df, pitching_df)

    if hitters_merged.empty and pitchers_merged.empty:
        st.warning("No stats found for Rule 5 eligible players. They may not have played in 2025 yet.")
        return

    # Tabs for hitters and pitchers (NO level breakdown here - it's in analytics now)
    tab1, tab2 = st.tabs(["Hitters", "Pitchers"])

    with tab1:
        if not hitters_merged.empty:
            display_basic_batting_stats(hitters_merged, min_pa=1)
        else:
            st.info("No batting stats available for eligible players")

    with tab2:
        if not pitchers_merged.empty:
            display_basic_pitching_stats(pitchers_merged, min_ip=1)
        else:
            st.info("No pitching stats available for eligible players")


def display_aaa_section(df: pd.DataFrame, savant_df: pd.DataFrame):
    """Display AAA players with advanced metrics."""
    from utils.constants import MIN_PA_THRESHOLD, MIN_IP_THRESHOLD

    merged_df = merge_rule5_with_savant(df, savant_df)

    if not merged_df.empty:
        st.subheader("AAA Players - Advanced Metrics")
        st.caption("Advanced statcast metrics from ProspectSavant")

        # Separate hitters and pitchers
        hitters_aaa = merged_df[merged_df["Player Type"] == "Hitter"].copy()
        pitchers_aaa = merged_df[merged_df["Player Type"] == "Pitcher"].copy()

        # Filter by minimum thresholds
        if not hitters_aaa.empty:
            hitters_aaa = hitters_aaa[hitters_aaa["PA"] >= MIN_PA_THRESHOLD]
        if not pitchers_aaa.empty:
            pitchers_aaa = pitchers_aaa[pitchers_aaa["IP"] >= MIN_IP_THRESHOLD]

        # Display tables
        if not hitters_aaa.empty:
            display_aaa_hitters_table(hitters_aaa)

        if not pitchers_aaa.empty:
            display_aaa_pitchers_table(pitchers_aaa)

        if hitters_aaa.empty and pitchers_aaa.empty:
            st.info(
                f"No AAA players meet the minimum thresholds "
                f"({MIN_PA_THRESHOLD} PA for hitters, {MIN_IP_THRESHOLD} IP for pitchers)"
            )
    else:
        st.info("No AAA Rule 5 eligible players found with advanced stats.")


def display_top_prospects_section(df: pd.DataFrame):
    """Display top prospects available."""
    st.subheader("Top Prospects Available")
    top_prospects = df[df["Org Rank"] <= MIN_ORG_RANK_FOR_TOP_PROSPECTS].sort_values("Org Rank")

    if not top_prospects.empty:
        st.write(f"**{len(top_prospects)} eligible top-{MIN_ORG_RANK_FOR_TOP_PROSPECTS} prospects**")
        display_top_prospects_table(top_prospects)
    else:
        st.info(f"No top-{MIN_ORG_RANK_FOR_TOP_PROSPECTS} prospects currently Rule 5 eligible")


def display_filters_and_table(df: pd.DataFrame):
    """Display search filters and main data table."""
    st.subheader("Search & Filters")

    # Player search
    search = st.text_input("Search by player name", placeholder="Enter player name...")

    # Filter controls
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        teams_filter = st.multiselect(
            "Filter by Team",
            options=sorted(df["Current Org"].unique()),
            default=None
        )

    with col2:
        position_filter = st.multiselect(
            "Filter by Position",
            options=sorted(df["Position"].unique()),
            default=None
        )

    with col3:
        level_filter = st.multiselect(
            "Filter by Level",
            options=sorted(df["Level"].dropna().unique()),
            default=None
        )

    with col4:
        if df["Age"].notna().any():
            min_age = int(df["Age"].min())
            max_age = int(df["Age"].max())
            age_range = st.slider("Filter by Age", min_age, max_age, (min_age, max_age))
        else:
            age_range = None

    # Apply filters
    filtered_df = apply_filters(df, search, teams_filter, position_filter, level_filter, age_range)

    # Sort by Org Rank, then Overall Rank
    filtered_df = filtered_df.sort_values(
        by=["Org Rank", "Overall Rank"],
        ascending=[True, True],
        na_position='last'
    )

    # Show filter summary
    if len(filtered_df) != len(df):
        st.info(f"📊 Showing {len(filtered_df)} of {len(df)} players after filters")

    st.divider()

    # Display main table
    st.subheader(f"All Eligible Players ({len(filtered_df)})")
    display_all_players_table(filtered_df)