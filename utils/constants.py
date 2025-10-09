"""Constants used throughout the application."""

# API Configuration
CACHE_TTL = 3600
REQUEST_TIMEOUT = 10
MAX_WORKERS = 5

# Thresholds
MIN_ORG_RANK_FOR_TOP_PROSPECTS = 10
MIN_PA_THRESHOLD = 50
MIN_IP_THRESHOLD = 20

# Team Mappings
TEAMS = {
    1: "LAA", 2: "BAL", 3: "BOS", 4: "CHW", 5: "CLE",
    6: "DET", 7: "KC", 8: "MIN", 9: "NYY", 10: "ATH",
    11: "SEA", 12: "TB", 13: "TEX", 14: "TOR", 15: "ARI",
    16: "ATL", 17: "CHC", 18: "CIN", 19: "COL", 20: "MIA",
    21: "HOU", 22: "LAD", 23: "MIL", 24: "WAS", 25: "NYM",
    26: "PHI", 27: "PIT", 28: "STL", 29: "SD", 30: "SF"
}

# API URLs
FANGRAPHS_ROSTER_URL = "https://www.fangraphs.com/api/depth-charts/roster"
PROSPECT_SAVANT_HITTERS_URL = "https://oriolebird.pythonanywhere.com/leaders/hitters/AAA/2025/0/16/28"
PROSPECT_SAVANT_PITCHERS_URL = "https://oriolebird.pythonanywhere.com/leaders/pitchers/AAA/2025/0/16/28"

# HTTP Headers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}