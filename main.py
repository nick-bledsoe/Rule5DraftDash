import streamlit as st
import requests
import pandas as pd
import time
from typing import Optional, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constants
MIN_ORG_RANK_FOR_TOP_PROSPECTS = 10
CACHE_TTL = 3600
REQUEST_TIMEOUT = 10
MAX_WORKERS = 5
MIN_PA_THRESHOLD = 50
MIN_IP_THRESHOLD = 20

st.set_page_config(
    page_title="Rule 5 Draft Dashboard",
    page_icon="rule-5-cutout.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar
st.markdown("""
<style>
    [data-testid="collapsedControl"] {
        display: none;
    }
    section[data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

teams = {
    1: "LAA", 2: "BAL", 3: "BOS", 4: "CHW", 5: "CLE",
    6: "DET", 7: "KC", 8: "MIN", 9: "NYY", 10: "ATH",
    11: "SEA", 12: "TB", 13: "TEX", 14: "TOR", 15: "ARI",
    16: "ATL", 17: "CHC", 18: "CIN", 19: "COL", 20: "MIA",
    21: "HOU", 22: "LAD", 23: "MIL", 24: "WAS", 25: "NYM",
    26: "PHI", 27: "PIT", 28: "STL", 29: "SD", 30: "SF"
}


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
    url = f"https://www.fangraphs.com/api/depth-charts/roster?teamid={teamid}&loaddate={int(time.time())}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    players = []

    try:
        res = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
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
            for teamid, team_abbr in teams.items()
        }

        completed = 0
        for future in as_completed(future_to_team):
            team_abbr = future_to_team[future]
            try:
                players = future.result()
                all_players.extend(players)
                completed += 1
                status_text.text(f"Fetching data... ({completed}/{len(teams)} teams)")
                progress_bar.progress(completed / len(teams))
            except Exception as e:
                st.error(f"Error processing {team_abbr}: {e}")

    progress_bar.empty()
    status_text.empty()

    df = pd.DataFrame(all_players)

    # Ensure all positions show only the primary position
    if not df.empty and 'Position' in df.columns:
        df['Position'] = df['Position'].apply(get_primary_position)

    return df, fetch_time


@st.cache_data(ttl=CACHE_TTL)
def fetch_prospect_savant_data() -> pd.DataFrame:
    """Fetch AAA hitters and pitchers data from ProspectSavant."""
    hitters_url = "https://oriolebird.pythonanywhere.com/leaders/hitters/AAA/2025/0/16/28"
    pitchers_url = "https://oriolebird.pythonanywhere.com/leaders/pitchers/AAA/2025/0/16/28"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    all_data = []

    # Fetch hitters
    try:
        res = requests.get(hitters_url, headers=headers, timeout=REQUEST_TIMEOUT)
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
        res = requests.get(pitchers_url, headers=headers, timeout=REQUEST_TIMEOUT)
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


def merge_rule5_with_savant(rule5_df: pd.DataFrame, savant_df: pd.DataFrame) -> pd.DataFrame:
    """Merge Rule 5 eligible players with ProspectSavant data."""
    aaa_rule5 = rule5_df[rule5_df["Level"] == "AAA"].copy()

    if aaa_rule5.empty or savant_df.empty:
        return pd.DataFrame()

    # Normalize names for matching
    aaa_rule5["name_norm"] = aaa_rule5["Player"].str.strip().str.lower()
    savant_df["name_norm"] = savant_df["Player"].str.strip().str.lower()

    merged = aaa_rule5.merge(savant_df, on="name_norm", how="inner", suffixes=("", "_savant"))
    merged = merged.drop(columns=["name_norm", "Age_savant", "Position_savant"], errors="ignore")

    return merged


# Initialize session state
if 'last_fetch_time' not in st.session_state:
    st.session_state.last_fetch_time = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Player Data"

# Top Navigation
st.image("rule-5-cutout.png")
st.markdown("## MLB Rule 5 Draft Dashboard")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("📊 Player Data", use_container_width=True,
                 type="primary" if st.session_state.current_page == "Player Data" else "secondary"):
        st.session_state.current_page = "Player Data"
        st.rerun()
with col2:
    if st.button("📚 About & History", use_container_width=True,
                 type="primary" if st.session_state.current_page == "About & History" else "secondary"):
        st.session_state.current_page = "About & History"
        st.rerun()
with col3:
    st.write("")  # Empty column for spacing

st.divider()

# ==================== PAGE: PLAYER DATA ====================
if st.session_state.current_page == "Player Data":
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

    if not df.empty:
        # Calculate metrics
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

        if st.session_state.last_fetch_time:
            st.caption(f"📅 Data fetched: {st.session_state.last_fetch_time}")

        st.divider()

        # AAA PLAYERS WITH ADVANCED STATS
        if not savant_df.empty:
            merged_df = merge_rule5_with_savant(df, savant_df)

            if not merged_df.empty:
                st.subheader("AAA Players - Advanced Metrics")
                st.caption("Data from ProspectSavant")

                # Separate hitters and pitchers
                hitters_aaa = merged_df[merged_df["Player Type"] == "Hitter"].copy()
                pitchers_aaa = merged_df[merged_df["Player Type"] == "Pitcher"].copy()

                # Filter by minimum thresholds
                if not hitters_aaa.empty:
                    hitters_aaa = hitters_aaa[hitters_aaa["PA"] >= MIN_PA_THRESHOLD]
                if not pitchers_aaa.empty:
                    pitchers_aaa = pitchers_aaa[pitchers_aaa["IP"] >= MIN_IP_THRESHOLD]

                if not hitters_aaa.empty:
                    st.write(f"**Hitters** (minimum {MIN_PA_THRESHOLD} PA)")
                    hitters_display = hitters_aaa[[
                        "Player", "Position", "Age", "Current Org", "Org Rank", "Prospect Score",
                        "PA", "xBA", "xwOBA", "xSLG", "Barrel%", "Chase%", "K%", "BB%", "EV", "Sprint Speed"
                    ]].sort_values("Org Rank", na_position='last')

                    st.dataframe(
                        hitters_display,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Prospect Score": st.column_config.NumberColumn("Prospect Score", format="%.1f%%",
                                                                            help="ProspectSavant overall score percentile"),
                            "EV": st.column_config.NumberColumn("EV", format="%.1f"),
                            "xBA": st.column_config.NumberColumn("xBA", format="%.3f"),
                            "xSLG": st.column_config.NumberColumn("xSLG", format="%.3f"),
                            "Barrel%": st.column_config.NumberColumn("Barrel%", format="%.1f%%"),
                            "Chase%": st.column_config.NumberColumn("Chase%", format="%.1f%%"),
                            "K%": st.column_config.NumberColumn("K%", format="%.1f%%"),
                            "BB%": st.column_config.NumberColumn("BB%", format="%.1f%%"),
                            "xwOBA": st.column_config.NumberColumn("xwOBA", format="%.3f"),
                            "Sprint Speed": st.column_config.NumberColumn("Sprint Speed", format="%.2f"),
                        }
                    )

                    # Download button for hitters
                    csv_hitters = hitters_display.to_csv(index=False)
                    st.download_button(
                        label="📥 Download AAA Hitters CSV",
                        data=csv_hitters,
                        file_name=f"rule5_aaa_hitters_{time.strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key="download_hitters"
                    )

                if not pitchers_aaa.empty:
                    st.write(f"**Pitchers** (minimum {MIN_IP_THRESHOLD} IP)")
                    pitchers_display = pitchers_aaa[[
                        "Player", "Position", "Age", "Current Org", "Org Rank", "Prospect Score",
                        "IP", "Max Velo", "xBA", "xwOBA", "xSLG", "K%", "BB%", "Chase%", "Whiff%"
                    ]].sort_values("Org Rank", na_position='last')

                    st.dataframe(
                        pitchers_display,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Prospect Score": st.column_config.NumberColumn("Prospect Score", format="%.1f%%",
                                                                            help="ProspectSavant overall score percentile"),
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

                    # Download button for pitchers
                    csv_pitchers = pitchers_display.to_csv(index=False)
                    st.download_button(
                        label="📥 Download AAA Pitchers CSV",
                        data=csv_pitchers,
                        file_name=f"rule5_aaa_pitchers_{time.strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key="download_pitchers"
                    )

                if hitters_aaa.empty and pitchers_aaa.empty:
                    st.info(
                        f"No AAA players meet the minimum thresholds ({MIN_PA_THRESHOLD} PA for hitters, {MIN_IP_THRESHOLD} IP for pitchers)")
            else:
                st.info(
                    "No AAA Rule 5 eligible players found with advanced stats.")

            st.divider()

        # TOP PROSPECTS SECTION
        st.subheader("Top Prospects Available")
        top_prospects = df[df["Org Rank"] <= MIN_ORG_RANK_FOR_TOP_PROSPECTS].sort_values("Org Rank")

        if not top_prospects.empty:
            st.write(f"**{len(top_prospects)} eligible top-{MIN_ORG_RANK_FOR_TOP_PROSPECTS} prospects**")

            st.dataframe(
                top_prospects,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Org Rank": st.column_config.NumberColumn("Org Rank", help="Organization ranking", format="%.0f"),
                    "Overall Rank": st.column_config.NumberColumn("Overall Rank", help="Overall level ranking",
                                                                  format="%.0f")
                }
            )

            # Download button for top prospects
            csv_top = top_prospects.to_csv(index=False)
            st.download_button(
                label="📥 Download Top Prospects CSV",
                data=csv_top,
                file_name=f"rule5_top_prospects_{time.strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="download_top"
            )
        else:
            st.info(f"No top-{MIN_ORG_RANK_FOR_TOP_PROSPECTS} prospects currently Rule 5 eligible")

        st.divider()

        # ANALYTICS SECTION
        st.subheader("Analytics & Insights")

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

        # Additional insights
        st.write("**Key Insights:**")
        col1, col2 = st.columns(2)
        with col1:
            young_prospects = len(df[df["Age"] <= 23])
            st.metric("Young Prospects (≤23)", young_prospects)
        with col2:
            ranked_prospects = len(df[df["Org Rank"] <= 20])
            st.metric("Top-20 Org Prospects", ranked_prospects)

        st.divider()

        # FILTERS SECTION
        st.subheader("Search & Filters")

        # Player search
        search = st.text_input("Search by player name", placeholder="Enter player name...")

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
        filtered_df = df.copy()

        if search:
            filtered_df = filtered_df[filtered_df["Player"].str.contains(search, case=False, na=False)]

        if teams_filter:
            filtered_df = filtered_df[filtered_df["Current Org"].isin(teams_filter)]

        if position_filter:
            filtered_df = filtered_df[filtered_df["Position"].isin(position_filter)]

        if level_filter:
            filtered_df = filtered_df[filtered_df["Level"].isin(level_filter)]

        if age_range:
            filtered_df = filtered_df[filtered_df["Age"].between(age_range[0], age_range[1])]

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

        # MAIN DATA TABLE
        st.subheader(f"All Eligible Players ({len(filtered_df)})")

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Org Rank": st.column_config.NumberColumn("Org Rank", help="Organization ranking", format="%.0f"),
                "Overall Rank": st.column_config.NumberColumn("Overall Rank",
                                                              help="Overall level ranking across all teams",
                                                              format="%.0f"),
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

    else:
        st.info("👆 Click the button above to fetch the latest Rule 5 eligible players")

    st.divider()
    st.caption("Prospect draft info and rankings courtesy of FanGraphs | Triple A advanced metrics and prospect scores courtesy of ProspectSavant")
    st.caption("Rule 5 Draft Dashboard is not affiliated with MLB, nor with any of their digital properties. All rights reserved.")

# ==================== PAGE: ABOUT & HISTORY ====================
elif st.session_state.current_page == "About & History":
    st.markdown("""
    ## What is the Rule 5 Draft?

    The Rule 5 Draft is an annual event held during MLB's Winter Meetings in December. It gives teams the opportunity 
    to select players from other organizations' minor league systems who are not on their 40-man roster.

    ### Key Rules & Requirements

    **Eligibility:**
    - Players signed at **age 18 or younger** must be protected after **5 years** in the organization
    - Players signed at **age 19 or older** must be protected after **4 years** in the organization
    - Players not added to the 40-man roster by these deadlines become eligible

    **Requirements:**
    - Selected players must remain on the selecting team's **26-man active roster for the entire season**
    - If the player cannot stay on the roster, they must be **offered back** to their original team for $50,000
    - The original team can reclaim the player or allow him to be placed on waivers

    **Draft Order:**
    - Major League phase: Reverse order of previous season's standings
    - Triple-A phase: Available for Triple-A affiliated teams
    - Double-A phase: Available for Double-A affiliated teams

    **Cost:**
    - **$100,000** per selection in the Major League phase
    - **$24,000** per selection in the Triple-A phase
    - **$12,000** per selection in the Double-A phase

    ---

    ## Historical Context

    The Rule 5 Draft was established in **1920** to prevent wealthy teams from hoarding talent in their minor league 
    systems. It has since become a valuable way for teams to find overlooked prospects and add depth to their rosters.

    ### Notable Rule 5 Success Stories

    Many successful MLB players have been selected in the Rule 5 Draft, including:

    - **Roberto Clemente** (1954) - Selected by Pittsburgh Pirates from Brooklyn Dodgers
    - **Johan Santana** (1999) - Selected by Minnesota Twins from Houston Astros
    - **Josh Hamilton** (2006) - Selected by Chicago Cubs from Tampa Bay Devil Rays
    - **José Bautista** (2003) - Selected by Baltimore Orioles from Pittsburgh Pirates

    ### Historical Statistics

    - **Average selections per year:** 10-15 players in the Major League phase
    - **Success rate:** Approximately 20-25% of selections stick with their new teams
    - **All-Star selections:** Over 50 Rule 5 picks have made at least one All-Star team

    ---

    ## About This App

    This application aggregates data from multiple sources to help identify potential Rule 5 Draft candidates:

    **Data Sources:**
    - **FanGraphs RosterResource** - 40-man roster status and organizational rankings
    - **ProspectSavant** - Advanced minor league metrics and performance data

    **Key Features:**
    - Real-time eligibility tracking across all 30 MLB organizations
    - Advanced metrics for AAA players (only level currently with statcast data)
    - Organizational rankings to identify high-value unprotected players
    - Comprehensive filtering and search capabilities
    - Downloadable datasets for further analysis

    **Limitations:**
    - Data is updated hourly via caching
    - Some players may be protected after data is fetched
    - Rankings and metrics are subject to change
    - Not all eligible players will be selected

    ---

    ## Resources & Further Reading

    - [MLB Official Rules - Rule 5 Draft](https://www.mlb.com/glossary/transactions/rule-5-draft)
    - [FanGraphs RosterResource](https://www.fangraphs.com/roster-resource)
    - [ProspectSavant Analytics](https://prospectsavant.com/)
    - [Baseball America - Rule 5 Coverage](https://www.baseballamerica.com/)

    ---

    **Last Updated:** October 2025
    """)

    st.divider()
    st.caption("Data from FanGraphs RosterResource + ProspectSavant")