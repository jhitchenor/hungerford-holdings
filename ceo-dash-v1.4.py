import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. GOOGLE SHEETS & DATA (Logic remains same as v3.8) ---
# [Insert previous get_gsheet, load_game_data, and save_game_data functions here]

# --- 2. ADVISOR IMAGE MAPPING ---
# Ensure these files are in an 'assets' folder in your repo
ADVISOR_IMAGES = {
    "Chief of Staff": "assets/cos.png",
    "Diary Secretary": "assets/diary.png",
    "Head of M&A": "assets/m_and_a.png",
    "Portfolio Manager": "assets/portfolio.png",
    "Performance Coach": "assets/coach.png"
}

# --- 3. UPDATED RENDER FUNCTION WITH PORTRAITS ---
def render_task_button(task_list, key_prefix, is_rp=False):
    sorted_tasks = sorted(task_list, key=lambda x: x['xp'])
    for t in sorted_tasks:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            label = f"{t['name']} (+{t['xp']} {'RP' if is_rp else 'XP'})"
            if st.button(label, key=f"{key_prefix}_{t['name']}", use_container_width=True):
                update_stat('rp' if is_rp else 'xp', t['xp'], is_urgent=t.get('urgent', False))
        with col2:
            if "advisor" in t:
                with st.popover("ℹ️"):
                    # Display the Advisor's Portrait
                    if t['advisor'] in ADVISOR_IMAGES:
                        st.image(ADVISOR_IMAGES[t['advisor']], use_container_width=True)
                    st.subheader(f"Memo from: {t['advisor']}")
                    st.markdown(f"*{t['advice']}*")

# --- 4. TASK DEFINITIONS (Expanded with your Tranche) ---
# [Insert the task lists from v3.8 here]

# --- 5. UI LAYOUT ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# Sidebar - MD Profile
with st.sidebar:
    # Optional: Put the Chief of Staff portrait here as the primary contact
    st.image("assets/cos.png", caption="Chief of Staff - Executive Office")
    st.title(f"🎖️ Level {st.session_state.game_data['level']}")
    # [Insert rest of sidebar logic from v3.8]

# [Insert Tabs and Main Dashboard logic from v3.8]
