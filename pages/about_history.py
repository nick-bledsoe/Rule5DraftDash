"""About & History page - educational content about Rule 5 Draft."""

import streamlit as st


def render():
    """Render the About & History page."""
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