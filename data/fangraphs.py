"""FanGraphs data fetching and processing."""

import time
import requests
import pandas as pd
import streamlit as st
from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.constants import (
    TEAMS, FANGRAPHS_ROSTER_URL, DEFAULT_HEADERS,
    REQUEST_TIMEOUT, MAX_WORKERS, CACHE_TTL
)


def normalize_numeric_column(value) -> Optional[float]:
    """Convert value to float, returning None if invalid."""
    try:
        return float(value) if value else None
    except (ValueError, TypeError):
        return None


def get_primary_position(position: str) -> str:
    """Extract the first position from a multi-position string."""
    if not position:
        return position
    # Split by common delimiters and return first position
    return position.split('/')[0].strip()


def fetch_team_data(teamid: int, team_abbr: str) -> List[Dict]:
    """Fetch Rule 5 eligible players for a single team."""
    url = f"{FANGRAPHS_ROSTER_URL}?teamid={teamid}&loaddate={int(time.time())}"

    players = []

    try:
        res = requests.get(url, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        res.raise_for_status()
        data = res.json()

        for p in data:
            if p.get("options") == "R5" or p.get("options1") == "R5":
                player_dict = {
                    "Player": p.get("player"),
                    "Position": get_primary_position(p.get("position")),
                    "Age": normalize_numeric_column(p.get("age")),
                    "Level": p.get("mlevel"),
                    "Current Org": team_abbr,
                    "Org Rank": normalize_numeric_column(p.get("Org_Rank_Next")),
                    "Overall Rank": normalize_numeric_column(p.get("Overall_Rank"))
                }
                players.append(player_dict)

    except requests.exceptions.RequestException as e:
        st.warning(f"Failed to fetch {team_abbr}: {e}")

    return players


@st.cache_data(ttl=CACHE_TTL)
def fetch_rule5_players() -> tuple[pd.DataFrame, str]:
    """Fetch all Rule 5 eligible players from FanGraphs."""
    all_players = []
    fetch_time = time.strftime('%Y-%m-%d %H:%M:%S')

    progress_bar = st.progress(0)
    status_text = st.empty()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_team = {
            executor.submit(fetch_team_data, teamid, team_abbr): team_abbr
            for teamid, team_abbr in TEAMS.items()
        }

        completed = 0
        for future in as_completed(future_to_team):
            team_abbr = future_to_team[future]
            try:
                players = future.result()
                all_players.extend(players)
                completed += 1
                status_text.text(f"Fetching data... ({completed}/{len(TEAMS)} teams)")
                progress_bar.progress(completed / len(TEAMS))
            except Exception as e:
                st.error(f"Error processing {team_abbr}: {e}")

    progress_bar.empty()
    status_text.empty()

    df = pd.DataFrame(all_players)

    # Ensure all positions show only the primary position
    if not df.empty and 'Position' in df.columns:
        df['Position'] = df['Position'].apply(get_primary_position)

    return df, fetch_time