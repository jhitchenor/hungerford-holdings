import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. DATA LOADING ---
def get_gsheet(sheet_name="Sheet1"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("your_key_file.json", scope)
        client = gspread.authorize(creds)
        SPREADSHEET_ID = "1wZSAKq283Q1xf9FAeMBIw403lpavRRAVLKNntc950Og" 
        return client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
    except: return None

def load_game_data():
    default_data = {"xp": 505, "rp": 0, "streak": 0, "level": 2}
    try:
        sheet = get_gsheet("Sheet1")
        if sheet:
            row = sheet.row_values(2)
            data = {"xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]), "level": int(row[4])}
            if data["xp"] >= 500 and data["level"] == 1: data["level"] = 2
            return data
        return default_data
    except: return default_data

if 'game_data' not in st.session_state:
    st.session_state.game_data = load_game_data()

def update_stat(stat, amount, is_urgent=False):
    multiplier = 1.5 if is_urgent else 1.0
    st.session_state.game_data[stat] += int(amount * multiplier)
    if st.session_state.game_data['xp'] >= (st.session_state.game_data['level'] * 500):
        st.session_state.game_data['level'] += 1
        st.balloons()
    # In a real app, you'd call save_game_data here
    st.rerun()

# --- 3. ADVISOR PROFILES & LIVE DIRECTIVES ---
ADVISORS = {
    "Chief of Staff": {
        "img": "assets/cos.png",
        "title": "Executive Office",
        "style": "Authoritative & Warm",
        "directive": "Jack, darling, we need that CCJ cleared. It's the only anchor holding the ship back. Let's make it our primary objective this week."
    },
    "Diary Secretary": {
        "img": "assets/diary.png",
        "title": "Operations",
        "style": "Crisp & Professional",
        "directive": "I've reviewed your logistics for the Hungerford deployment. Ensure the CR-V is checked today. No excuses for mechanical failure."
    },
    "Head of M&A": {
        "img": "assets/m_and_a.png",
        "title": "Growth & Partnerships",
        "style": "Flirty & Strategic",
        "directive": "Harrow is lovely, but you're a Central London man at heart, handsome. Let's find an acquisition (a date) in the West End this weekend."
    },
    "Portfolio Manager": {
        "img": "assets/portfolio.png",
        "title": "Finance & Treasury",
        "style": "Analytical & Precise",
        "directive": "The numbers don't lie. If we don't update that budget tracker, we're flying blind. 5 minutes of data entry for total clarity."
    },
    "Performance Coach": {
        "img": "assets/coach.png",
        "title": "Human Capital",
        "style": "Bubbly & Energetic",
        "directive": "Let's go, Champ! That golf swing needs a flexible T-spine. Give me 15 minutes of stretching and feel the power!"
    }
}

# --- 4. THE TASK RENDERER ---
def render_task_section(task_list, key_prefix, is_rp=False):
    sorted_tasks = sorted(task_list, key=lambda x: x['xp'])
    for t in sorted_tasks:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            label = f"{t['name']} (+{t['xp']} {'RP' if is_rp else 'XP'})"
            if st.button(label, key=f"{key_prefix}_{t['name']}", use_container_width=True):
                update_stat('rp' if is_rp else 'xp', t['xp'], is_urgent=t.get('urgent', False))
        with col2:
            with st.popover("🗨️"):
                adv = t['advisor']
                st.image(ADVISORS[adv]['img'], use_container_width=True)
                st.subheader(f"Memo: {adv}")
                st.write(f"*{t['advice']}*")

# --- 5. TASK LIBRARIES (With "Voices") ---
daily_ops = [
    {"name": "Skincare Routine", "xp": 10, "advisor": "Chief of Staff", "advice": "We must maintain the brand, Jack. Looking the part is half the battle."},
    {"name": "Supplement Stack", "xp": 10, "advisor": "Performance Coach", "advice": "Fuel your brain, Champ! Those Omega-3s are like high-octane petrol for your mind!"},
    {"name": "15 mins stretching", "xp": 15, "advisor": "Performance Coach", "advice": "Deep breaths! Let's get that rotation back so you can crush it on the fairway!"},
]

m_a_tasks = [
    {"name": "Active Networking (Apps)", "xp": 30, "advisor": "Head of M&A", "advice": "Don't be shy, handsome. Put yourself out there—the 'market' is waiting for a man like you."},
    {"name": "Central London Venture", "xp": 150, "advisor": "Head of M&A", "advice": "A change of scenery is so refreshing. Let's find a chic little spot in Marylebone and see who catches your eye."},
]

# ... [Include other task lists here following the same advisor/advice structure] ...

# --- 6. UI LAYOUT ---
with st.sidebar:
    st.image(ADVISORS["Chief of Staff"]["img"])
    st.title(f"Level {st.session_state.game_data['level']}")
    # ... [Sidebar stats logic] ...

tabs = st.tabs(["🏛️ Boardroom", "🚨 Critical Path", "⚡ Daily Ops", "💼 Projects", "🥂 M&A", "👴 Stakeholders"])

with tabs[0]:
    st.header("Board of Directors")
    cols = st.columns(5)
    for i, (name, info) in enumerate(ADVISORS.items()):
        with cols[i]:
            st.image(info['img'], use_container_width=True)
            st.button(f"Briefing: {name}", key=f"btn_{name}")
            st.info(info['directive'])

# [Remaining tab rendering using render_task_section]
