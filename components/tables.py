"""Reusable table display components - All tables in one file."""

import streamlit as st
import pandas as pd
import time

from utils.styling import apply_gradient_styling
from utils.constants import MIN_PA_THRESHOLD, MIN_IP_THRESHOLD


# ============================================================================
# AAA ADVANCED STATS TABLES (ProspectSavant - with gradient styling)
# ============================================================================

def display_aaa_hitters_table(hitters_df: pd.DataFrame):
    """Display AAA hitters table with advanced metrics."""
    st.write(f"**Hitters** (minimum {MIN_PA_THRESHOLD} PA)")
    st.caption("Green (best) -> Red (worst) - Gradient shows relative performance among eligible players")

    hitters_display = hitters_df[[
        "Player", "Position", "Age", "Current Org", "Org Rank", "Prospect Score",
        "PA", "xBA", "xwOBA", "xSLG", "Barrel%", "Chase%", "K%", "BB%", "EV", "Sprint Speed"
    ]].sort_values("Prospect Score", ascending=False, na_position='last')

    # Keep original for download
    hitters_download = hitters_display.copy()

    # Apply gradient styling for display
    hitters_styled = apply_gradient_styling(hitters_display, "Hitter")

    st.dataframe(
        hitters_styled,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Age": st.column_config.NumberColumn("Age", format="%.1f"),
            "Org Rank": st.column_config.NumberColumn("Org Rank", format="%.0f"),
            "Prospect Score": st.column_config.NumberColumn(
                "Prospect Score",
                format="%.1f%%",
                help="ProspectSavant overall score percentile"
            ),
            "PA": st.column_config.NumberColumn("PA", format="%.0f"),
            "EV": st.column_config.NumberColumn("EV", format="%.1f"),
            "xBA": st.column_config.NumberColumn("xBA", format="%.3f"),
            "xSLG": st.column_config.NumberColumn("xSLG", format="%.3f"),
            "Barrel%": st.column_config.NumberColumn("Barrel%", format="%.1f%%"),
            "Chase%": st.column_config.NumberColumn("Chase%", format="%.1f%%"),
            "K%": st.column_config.NumberColumn("K%", format="%.1f%%"),
            "BB%": st.column_config.NumberColumn("BB%", format="%.1f%%"),
            "xwOBA": st.column_config.NumberColumn("xwOBA", format="%.3f"),
            "Sprint Speed": st.column_config.NumberColumn("Speed Score", format="%.2f"),
        }
    )

    # Download button
    csv_hitters = hitters_download.to_csv(index=False)
    st.download_button(
        label="📥 Download AAA Hitters CSV",
        data=csv_hitters,
        file_name=f"rule5_aaa_hitters_{time.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="download_hitters"
    )


def display_aaa_pitchers_table(pitchers_df: pd.DataFrame):
    """Display AAA pitchers table with advanced metrics."""
    st.write(f"**Pitchers** (minimum {MIN_IP_THRESHOLD} IP)")
    st.caption("Green (best) -> Red (worst) - Gradient shows relative performance among eligible players")

    pitchers_display = pitchers_df[[
        "Player", "Position", "Age", "Current Org", "Org Rank", "Prospect Score",
        "IP", "Max Velo", "xBA", "xwOBA", "xSLG", "K%", "BB%", "Chase%", "Whiff%"
    ]].sort_values("Prospect Score", ascending=False, na_position='last')

    # Keep original for download
    pitchers_download = pitchers_display.copy()

    # Apply gradient styling for display
    pitchers_styled = apply_gradient_styling(pitchers_display, "Pitcher")

    st.dataframe(
        pitchers_styled,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Age": st.column_config.NumberColumn("Age", format="%.1f"),
            "Org Rank": st.column_config.NumberColumn("Org Rank", format="%.0f"),
            "Prospect Score": st.column_config.NumberColumn(
                "Prospect Score",
                format="%.1f%%",
                help="ProspectSavant overall score percentile"
            ),
            "IP": st.column_config.NumberColumn("IP", format="%.1f"),
            "Max Velo": st.column_config.NumberColumn("Max Velo", format="%.1f"),
            "xBA": st.column_config.NumberColumn("xBA", format="%.3f"),
            "xSLG": st.column_config.NumberColumn("xSLG", format="%.3f"),
            "K%": st.column_config.NumberColumn("K%", format="%.1f%%"),
            "BB%": st.column_config.NumberColumn("BB%", format="%.1f%%"),
            "Chase%": st.column_config.NumberColumn("Chase%", format="%.1f%%"),
            "Whiff%": st.column_config.NumberColumn("Whiff%", format="%.1f%%"),
            "xwOBA": st.column_config.NumberColumn("xwOBA", format="%.3f"),
        }
    )

    # Download button
    csv_pitchers = pitchers_download.to_csv(index=False)
    st.download_button(
        label="📥 Download AAA Pitchers CSV",
        data=csv_pitchers,
        file_name=f"rule5_aaa_pitchers_{time.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="download_pitchers"
    )


# ============================================================================
# BASIC STATS TABLES (FanGraphs - All Levels)
# ============================================================================

def display_basic_batting_stats(df: pd.DataFrame, min_pa: int = 1):
    """
    Display basic batting stats for Rule 5 eligible players.

    Args:
        df: DataFrame with merged Rule 5 + batting stats
        min_pa: Minimum plate appearances to display
    """
    if df.empty:
        st.info("No batting stats available for Rule 5 eligible players")
        return

    # Filter by PA
    if 'PA' in df.columns:
        df = df[df['PA'] >= min_pa].copy()

    if df.empty:
        st.info(f"No hitters with minimum {min_pa} PA")
        return

    st.write(f"**{len(df)} Hitters with {min_pa}+ PA**")

    # Select display columns
    display_cols = [
        'Player', 'Age', 'aLevel', 'Current Org', 'Org Rank',
        'G', 'PA', 'AVG', 'OBP', 'SLG', 'OPS', 'HR', 'SB',
        'BB%', 'K%', 'wRC+'
    ]

    # Only use columns that exist
    available_cols = [col for col in display_cols if col in df.columns]
    display_df = df[available_cols].sort_values('Org Rank', na_position='last')

    # Format percentage columns (they come as decimals from API)
    if 'BB%' in display_df.columns:
        display_df['BB%'] = (display_df['BB%'] * 100).round(1)
    if 'K%' in display_df.columns:
        display_df['K%'] = (display_df['K%'] * 100).round(1)
    if 'wRC+' in display_df.columns:
        display_df['wRC+'] = display_df['wRC+'].round(0)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Age': st.column_config.NumberColumn('Age', format='%.0f'),
            'aLevel': st.column_config.TextColumn('Level'),
            'Org Rank': st.column_config.NumberColumn('Org Rank', format='%.0f'),
            'G': st.column_config.NumberColumn('G', format='%.0f'),
            'PA': st.column_config.NumberColumn('PA', format='%.0f'),
            'AVG': st.column_config.NumberColumn('AVG', format='%.3f'),
            'OBP': st.column_config.NumberColumn('OBP', format='%.3f'),
            'SLG': st.column_config.NumberColumn('SLG', format='%.3f'),
            'OPS': st.column_config.NumberColumn('OPS', format='%.3f'),
            'HR': st.column_config.NumberColumn('HR', format='%.0f'),
            'SB': st.column_config.NumberColumn('SB', format='%.0f'),
            'BB%': st.column_config.NumberColumn('BB%', format='%.1f%%'),
            'K%': st.column_config.NumberColumn('K%', format='%.1f%%'),
            'wRC+': st.column_config.NumberColumn('wRC+', format='%.0f', help='Weighted Runs Created Plus (100 = average)'),
        }
    )

    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Batting Stats CSV",
        data=csv,
        file_name=f"rule5_batting_stats_{time.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="download_basic_batting"
    )


def display_basic_pitching_stats(df: pd.DataFrame, min_ip: int = 1):
    """
    Display basic pitching stats for Rule 5 eligible players.

    Args:
        df: DataFrame with merged Rule 5 + pitching stats
        min_ip: Minimum innings pitched to display
    """
    if df.empty:
        st.info("No pitching stats available for Rule 5 eligible players")
        return

    # Filter by IP
    if 'IP' in df.columns:
        df = df[df['IP'] >= min_ip].copy()

    if df.empty:
        st.info(f"No pitchers with minimum {min_ip} IP")
        return

    st.write(f"**{len(df)} Pitchers with {min_ip}+ IP**")

    # Select display columns based on FanGraphs API structure
    display_cols = [
        'Player', 'Age', 'aLevel', 'Current Org', 'Org Rank',
        'G', 'GS', 'IP', 'W', 'L', 'SV', 'Hld',
        'ERA', 'WHIP', 'FIP', 'xFIP',
        'K/9', 'BB/9', 'HR/9', 'K-BB%',
        'K%', 'BB%', 'GB%', 'HR/FB', 'LOB%'
    ]

    # Only use columns that exist
    available_cols = [col for col in display_cols if col in df.columns]
    display_df = df[available_cols].sort_values('Org Rank', na_position='last')

    # Format percentage columns (they come as decimals from API)
    if 'K%' in display_df.columns:
        display_df['K%'] = (display_df['K%'] * 100).round(1)
    if 'BB%' in display_df.columns:
        display_df['BB%'] = (display_df['BB%'] * 100).round(1)
    if 'GB%' in display_df.columns:
        display_df['GB%'] = (display_df['GB%'] * 100).round(1)
    if 'HR/FB' in display_df.columns:
        display_df['HR/FB'] = (display_df['HR/FB'] * 100).round(1)
    if 'LOB%' in display_df.columns:
        display_df['LOB%'] = (display_df['LOB%'] * 100).round(1)
    if 'K-BB%' in display_df.columns:
        display_df['K-BB%'] = (display_df['K-BB%'] * 100).round(1)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Age': st.column_config.NumberColumn('Age', format='%.0f'),
            'aLevel': st.column_config.TextColumn('Level'),
            'Org Rank': st.column_config.NumberColumn('Org Rank', format='%.0f'),
            'G': st.column_config.NumberColumn('G', format='%.0f'),
            'GS': st.column_config.NumberColumn('GS', format='%.0f'),
            'IP': st.column_config.NumberColumn('IP', format='%.1f'),
            'W': st.column_config.NumberColumn('W', format='%.0f'),
            'L': st.column_config.NumberColumn('L', format='%.0f'),
            'SV': st.column_config.NumberColumn('SV', format='%.0f'),
            'Hld': st.column_config.NumberColumn('HLD', format='%.0f'),
            'ERA': st.column_config.NumberColumn('ERA', format='%.2f'),
            'WHIP': st.column_config.NumberColumn('WHIP', format='%.2f'),
            'FIP': st.column_config.NumberColumn('FIP', format='%.2f', help='Fielding Independent Pitching'),
            'xFIP': st.column_config.NumberColumn('xFIP', format='%.2f', help='Expected FIP'),
            'K/9': st.column_config.NumberColumn('K/9', format='%.2f'),
            'BB/9': st.column_config.NumberColumn('BB/9', format='%.2f'),
            'HR/9': st.column_config.NumberColumn('HR/9', format='%.2f'),
            'K-BB%': st.column_config.NumberColumn('K-BB%', format='%.1f%%', help='Strikeout rate minus walk rate'),
            'K%': st.column_config.NumberColumn('K%', format='%.1f%%'),
            'BB%': st.column_config.NumberColumn('BB%', format='%.1f%%'),
            'GB%': st.column_config.NumberColumn('GB%', format='%.1f%%', help='Ground ball percentage'),
            'HR/FB': st.column_config.NumberColumn('HR/FB', format='%.1f%%', help='Home runs per fly ball'),
            'LOB%': st.column_config.NumberColumn('LOB%', format='%.1f%%', help='Left on base percentage'),
        }
    )

    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Pitching Stats CSV",
        data=csv,
        file_name=f"rule5_pitching_stats_{time.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="download_basic_pitching"
    )


def display_level_breakdown(batting_df: pd.DataFrame, pitching_df: pd.DataFrame):
    """Display a breakdown of players by level."""

    st.subheader("Players by Level")

    col1, col2 = st.columns(2)

    with col1:
        if not batting_df.empty and 'aLevel' in batting_df.columns:
            st.write("**Hitters**")
            level_counts = batting_df['aLevel'].value_counts()
            st.bar_chart(level_counts)
        else:
            st.write("**Hitters**: No data")

    with col2:
        if not pitching_df.empty and 'aLevel' in pitching_df.columns:
            st.write("**Pitchers**")
            level_counts = pitching_df['aLevel'].value_counts()
            st.bar_chart(level_counts)
        else:
            st.write("**Pitchers**: No data")


# ============================================================================
# OTHER TABLES
# ============================================================================

def display_top_prospects_table(top_prospects_df: pd.DataFrame):
    """Display top prospects table."""
    st.dataframe(
        top_prospects_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Org Rank": st.column_config.NumberColumn(
                "Org Rank",
                help="Organization ranking",
                format="%.0f"
            ),
            "Overall Rank": st.column_config.NumberColumn(
                "Ovr MiLB Rank",
                help="Overall MiLB ranking",
                format="%.0f"
            )
        }
    )

    # Download button
    csv_top = top_prospects_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Top Prospects CSV",
        data=csv_top,
        file_name=f"rule5_top_prospects_{time.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="download_top"
    )


def display_all_players_table(filtered_df: pd.DataFrame):
    """Display main all players table."""
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Org Rank": st.column_config.NumberColumn(
                "Org Rank",
                help="Organization ranking",
                format="%.0f"
            ),
            "Overall Rank": st.column_config.NumberColumn(
                "Ovr MiLB Rank",
                help="Overall MiLB ranking",
                format="%.0f"
            ),
            "Age": st.column_config.NumberColumn("Age", format="%.1f")
        }
    )

    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download All Filtered Data as CSV",
        data=csv,
        file_name=f"rule5_eligible_players_{time.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="download_all"
    )