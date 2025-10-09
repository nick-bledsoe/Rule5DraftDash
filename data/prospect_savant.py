"""ProspectSavant data fetching and processing."""

import requests
import pandas as pd
import streamlit as st

from utils.constants import (
    PROSPECT_SAVANT_HITTERS_URL,
    PROSPECT_SAVANT_PITCHERS_URL,
    DEFAULT_HEADERS,
    REQUEST_TIMEOUT,
    CACHE_TTL
)
from data.fangraphs import get_primary_position


@st.cache_data(ttl=CACHE_TTL)
def fetch_prospect_savant_data() -> pd.DataFrame:
    """Fetch AAA hitters and pitchers data from ProspectSavant."""
    all_data = []

    # Fetch hitters
    try:
        res = requests.get(PROSPECT_SAVANT_HITTERS_URL, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        res.raise_for_status()
        hitters_data = res.json()

        if "data" in hitters_data:
            for player in hitters_data["data"]:
                score_p = player.get("score_p")
                prospect_score = score_p * 100 if score_p is not None else None

                all_data.append({
                    "Player": player.get("name"),
                    "Age": player.get("age"),
                    "Position": get_primary_position(player.get("Position")),
                    "Prospect Score": prospect_score,
                    "xBA": player.get("xba"),
                    "xSLG": player.get("xslg"),
                    "EV": player.get("ev"),
                    "Barrel%": player.get("barrelpa"),
                    "Chase%": player.get("chaserate"),
                    "K%": player.get("krate"),
                    "BB%": player.get("bbrate"),
                    "xwOBA": player.get("xwoba"),
                    "Sprint Speed": player.get("spd"),
                    "PA": player.get("pa"),
                    "Player Type": "Hitter"
                })
    except requests.exceptions.RequestException as e:
        st.warning(f"Failed to fetch ProspectSavant hitters: {e}")

    # Fetch pitchers
    try:
        res = requests.get(PROSPECT_SAVANT_PITCHERS_URL, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        res.raise_for_status()
        pitchers_data = res.json()

        if "data" in pitchers_data:
            for player in pitchers_data["data"]:
                score_p = player.get("score_p")
                prospect_score = score_p * 100 if score_p is not None else None

                all_data.append({
                    "Player": player.get("name"),
                    "Age": player.get("age"),
                    "Position": get_primary_position(player.get("Position", "P")),
                    "Prospect Score": prospect_score,
                    "Max Velo": player.get("max_velo"),
                    "xBA": player.get("xba"),
                    "xSLG": player.get("xslg"),
                    "K%": player.get("krate"),
                    "BB%": player.get("bbrate"),
                    "Chase%": player.get("chaserate"),
                    "xwOBA": player.get("xwoba"),
                    "Whiff%": player.get("whiffrate"),
                    "IP": player.get("ip"),
                    "Player Type": "Pitcher"
                })
    except requests.exceptions.RequestException as e:
        st.warning(f"Failed to fetch ProspectSavant pitchers: {e}")

    return pd.DataFrame(all_data)