"""Fetch minor league stats from FanGraphs API."""

import requests
import pandas as pd
import streamlit as st
import re
from typing import Optional

from utils.constants import DEFAULT_HEADERS, REQUEST_TIMEOUT, CACHE_TTL


# League IDs (from the URL you provided)
LEAGUE_IDS = {
    'AAA': '11',  # Triple-A
    'AA': '12',   # Double-A
    'A+': '13',   # High-A
    'A': '14',    # Single-A
    'ALL': '2,4,5,6,7,8,9,10,11,14,12,13,15,16,17,18,30,32'  # All leagues
}

# Level codes
LEVEL_CODES = {
    'AAA': '11',
    'AA': '12',
    'A+': '13',
    'A': '14',
    'ALL': '0'  # 0 = all levels
}


def clean_player_name(name: str) -> str:
    """
    Clean player name by removing HTML tags and extra whitespace.
    FanGraphs returns names like: <a href="...">Jon Singleton</a>
    """
    if not name or not isinstance(name, str):
        return ""

    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', name)
    return clean.strip()


@st.cache_data(ttl=CACHE_TTL)
def fetch_minors_batting_stats(season: int = 2025, level: str = 'ALL', min_pa: int = 0) -> pd.DataFrame:
    """
    Fetch minor league batting statistics from FanGraphs.

    Args:
        season: Season year (default 2025)
        level: 'AAA', 'AA', 'A+', 'A', or 'ALL' (default 'ALL')
        min_pa: Minimum plate appearances (0 = no minimum)

    Returns:
        DataFrame with batting statistics
    """
    url = "https://www.fangraphs.com/api/leaders/minor-league/data"

    params = {
        'pos': 'all',
        'level': LEVEL_CODES.get(level, '0'),
        'lg': LEAGUE_IDS.get(level, LEAGUE_IDS['ALL']),
        'stats': 'bat',  # batting stats
        'qual': '0',
        'type': '0',  # Season stats
        'team': '',
        'season': str(season),
        'seasonEnd': str(season),
        'org': '',
        'ind': '0',
        'splitTeam': 'false'
    }

    try:
        response = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()

        # The response should be a list of player dictionaries or a dict with 'data' key
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and 'data' in data:
            df = pd.DataFrame(data['data'])
        else:
            st.warning(f"Unexpected data format from FanGraphs batting API")
            return pd.DataFrame()

        # Clean player names
        if 'PlayerName' in df.columns:
            df['PlayerName'] = df['PlayerName'].apply(clean_player_name)

        # Filter by minimum PA if specified
        if min_pa > 0 and 'PA' in df.columns:
            df = df[df['PA'] >= min_pa]

        return df

    except requests.exceptions.RequestException as e:
        st.warning(f"Failed to fetch batting stats: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"Error processing batting stats: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=CACHE_TTL)
def fetch_minors_pitching_stats(season: int = 2025, level: str = 'ALL', min_ip: int = 0) -> pd.DataFrame:
    """
    Fetch minor league pitching statistics from FanGraphs.

    Args:
        season: Season year (default 2025)
        level: 'AAA', 'AA', 'A+', 'A', or 'ALL' (default 'ALL')
        min_ip: Minimum innings pitched (0 = no minimum)

    Returns:
        DataFrame with pitching statistics
    """
    url = "https://www.fangraphs.com/api/leaders/minor-league/data"

    params = {
        'pos': 'all',
        'level': LEVEL_CODES.get(level, '0'),
        'lg': LEAGUE_IDS.get(level, LEAGUE_IDS['ALL']),
        'stats': 'pit',  # pitching stats
        'qual': '0',  # Qualified players only (matches your working URL)
        'type': '0',  # Season stats
        'team': '',
        'season': str(season),
        'seasonEnd': str(season),
        'org': '',
        'ind': '0',
        'splitTeam': 'false'
    }

    try:
        response = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()

        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and 'data' in data:
            df = pd.DataFrame(data['data'])
        else:
            st.warning(f"Unexpected data format from FanGraphs pitching API")
            return pd.DataFrame()

        # Clean player names
        if 'PlayerName' in df.columns:
            df['PlayerName'] = df['PlayerName'].apply(clean_player_name)

        # Filter by minimum IP if specified
        if min_ip > 0 and 'IP' in df.columns:
            df = df[df['IP'] >= min_ip]

        return df

    except requests.exceptions.RequestException as e:
        st.warning(f"Failed to fetch pitching stats: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"Error processing pitching stats: {e}")
        return pd.DataFrame()


def merge_rule5_with_minors_stats(rule5_df: pd.DataFrame, batting_df: pd.DataFrame,
                                   pitching_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Merge Rule 5 eligible players with minor league stats from FanGraphs.

    Args:
        rule5_df: DataFrame of Rule 5 eligible players
        batting_df: DataFrame of minor league batting stats
        pitching_df: DataFrame of minor league pitching stats

    Returns:
        Tuple of (hitters_merged, pitchers_merged)
    """
    if rule5_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Normalize player names for matching
    rule5_df = rule5_df.copy()
    rule5_df['name_norm'] = rule5_df['Player'].str.strip().str.lower()

    # Merge hitters
    hitters_merged = pd.DataFrame()
    if not batting_df.empty and 'PlayerName' in batting_df.columns:
        batting_df = batting_df.copy()

        # Normalize names for matching
        batting_df['name_norm'] = batting_df['PlayerName'].str.strip().str.lower()

        hitters_merged = rule5_df.merge(
            batting_df,
            on='name_norm',
            how='inner',
            suffixes=('', '_fg')
        )
        hitters_merged = hitters_merged.drop(columns=['name_norm'], errors='ignore')

        # Clean up aLevel - take only the highest level if multiple (e.g., "AA,AAA" -> "AAA")
        if 'aLevel' in hitters_merged.columns:
            hitters_merged['aLevel'] = hitters_merged['aLevel'].apply(get_highest_level)

    # Merge pitchers
    pitchers_merged = pd.DataFrame()
    if not pitching_df.empty and 'PlayerName' in pitching_df.columns:
        pitching_df = pitching_df.copy()

        # Normalize names for matching
        pitching_df['name_norm'] = pitching_df['PlayerName'].str.strip().str.lower()

        pitchers_merged = rule5_df.merge(
            pitching_df,
            on='name_norm',
            how='inner',
            suffixes=('', '_fg')
        )
        pitchers_merged = pitchers_merged.drop(columns=['name_norm'], errors='ignore')

        # Clean up aLevel - take only the highest level if multiple
        if 'aLevel' in pitchers_merged.columns:
            pitchers_merged['aLevel'] = pitchers_merged['aLevel'].apply(get_highest_level)

    return hitters_merged, pitchers_merged


def get_highest_level(level_str: str) -> str:
    """
    Extract the highest level from a comma-separated list.
    E.g., "AA,AAA" -> "AAA"

    Args:
        level_str: Level string (e.g., "AAA" or "AA,AAA")

    Returns:
        Highest level as string
    """
    if not level_str or not isinstance(level_str, str):
        return level_str

    # Level hierarchy (highest to lowest)
    level_order = ['AAA', 'AA', 'A+', 'A', 'Rk', 'FRk']

    # Split by comma and strip whitespace
    levels = [l.strip() for l in level_str.split(',')]

    # Return the highest level found
    for level in level_order:
        if level in levels:
            return level

    # If no match, return original
    return level_str


@st.cache_data(ttl=CACHE_TTL)
def get_all_minors_stats(season: int = 2025) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetch all minor league batting and pitching stats for the season.
    If fetching all levels fails, fetch each level separately.

    Args:
        season: Season year

    Returns:
        Tuple of (batting_df, pitching_df)
    """
    # Try fetching all levels at once first
    with st.spinner("Fetching minor league batting stats..."):
        batting_df = fetch_minors_batting_stats(season=season, level='ALL', min_pa=0)

    with st.spinner("Fetching minor league pitching stats..."):
        pitching_df = fetch_minors_pitching_stats(season=season, level='ALL', min_ip=0)

    # If that didn't work, try fetching each level separately
    if batting_df.empty:
        st.info("Fetching stats by level (this may take a moment)...")
        all_batting = []
        for level in ['AAA', 'AA', 'A+', 'A']:
            level_df = fetch_minors_batting_stats(season=season, level=level, min_pa=0)
            if not level_df.empty:
                all_batting.append(level_df)

        if all_batting:
            batting_df = pd.concat(all_batting, ignore_index=True)

    if pitching_df.empty:
        all_pitching = []
        for level in ['AAA', 'AA', 'A+', 'A']:
            level_df = fetch_minors_pitching_stats(season=season, level=level, min_ip=0)
            if not level_df.empty:
                all_pitching.append(level_df)

        if all_pitching:
            pitching_df = pd.concat(all_pitching, ignore_index=True)

    return batting_df, pitching_df


def get_player_stats_by_name(player_name: str, batting_df: pd.DataFrame,
                             pitching_df: pd.DataFrame) -> Optional[pd.Series]:
    """
    Get stats for a specific player by name.

    Args:
        player_name: Player's name
        batting_df: DataFrame of batting stats
        pitching_df: DataFrame of pitching stats

    Returns:
        Series with player stats or None if not found
    """
    name_norm = player_name.strip().lower()

    # Check batting
    if not batting_df.empty and 'PlayerName' in batting_df.columns:
        batting_match = batting_df[batting_df['PlayerName'].str.strip().str.lower() == name_norm]
        if not batting_match.empty:
            return batting_match.iloc[0]

    # Check pitching
    if not pitching_df.empty and 'PlayerName' in pitching_df.columns:
        pitching_match = pitching_df[pitching_df['PlayerName'].str.strip().str.lower() == name_norm]
        if not pitching_match.empty:
            return pitching_match.iloc[0]

    return None