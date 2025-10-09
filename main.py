"""Rule 5 Draft Dashboard - Main Entry Point"""

import streamlit as st

# Import page modules
from pages import player_data, about_history

# Page configuration
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

# Initialize session state
if 'last_fetch_time' not in st.session_state:
    st.session_state.last_fetch_time = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Player Data"

# Header and Navigation
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

# Route to appropriate page
if st.session_state.current_page == "Player Data":
    player_data.render()
elif st.session_state.current_page == "About & History":
    about_history.render()