import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. GOOGLE SHEETS ENGINE ---
def get_gsheet(sheet_name="Sheet1"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("your_key_file.json", scope)
    client = gspread.authorize(creds)
    SPREADSHEET_ID = "1wZSAKq283Q1xf9FAeMBIw403lpavRRAVLKNntc950Og" 
    return client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)

def load_game_data():
    try:
        sheet = get_gsheet("Sheet1")
        row = sheet.row_values(2)
        # Columns: A:Date, B:XP, C:RP, D:Streak, E:SocialRep, F:Level
        return {"xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]), "social_rep": int(row[4]), "level": int(row[5])}
    except:
        return {"xp": 0, "rp": 0, "streak": 0, "social_rep": 0, "level": 1}

def save_game_data(data):
    sheet1 = get_gsheet("Sheet1")
    sheet1.update('B2:F2', [[data['xp'], data['rp'], data['streak'], data['social_rep'], data['level']]])
    try:
        history_sheet = get_gsheet("XP_History")
        history_sheet.append_row([str(date.today()), data['xp']])
    except: pass

# --- 2. INITIALIZATION ---
if 'game_data' not in st.session_state:
    st.session_state.game_data = load_game_data()

def update_stat(stat, amount, is_urgent=False):
    multiplier = 1.5 if is_urgent else 1.0
    final_amount = int(amount * multiplier)
    st.session_state.game_data[stat] += final_amount
    
    # Level Up Logic
    xp_needed = st.session_state.game_data['level'] * 500
    if st.session_state.game_data['xp'] >= xp_needed:
        st.session_state.game_data['level'] += 1
        st.balloons()
        st.success(f"PROMOTED! You are now a Level {st.session_state.game_data['level']} Executive.")
        
    save_game_data(st.session_state.game_data)
    st.toast(f"📈 {stat.upper()} +{final_amount}")

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# Sidebar with Progress Bar
with sidebar:
    st.title(f"🎖️ Level {st.session_state.game_data['level']}")
    titles = ["Junior Associate", "Senior Analyst", "Associate Director", "Partner", "Managing Director"]
    title_idx = min(st.session_state.game_data['level'] - 1, len(titles)-1)
    st.caption(f"Rank: {titles[title_idx]}")
    
    # Progress Bar
    current_xp = st.session_state.game_data['xp']
    next_level_xp = st.session_state.game_data['level'] * 500
    prev_level_xp = (st.session_state.game_data['level'] - 1) * 500
    progress = (current_xp - prev_level_xp) / (next_level_xp - prev_level_xp)
    st.progress(min(max(progress, 0.0), 1.0))
    st.write(f"{current_xp} / {next_level_xp} XP to next Promotion")
    
    st.divider()
    st.metric("Corporate XP", st.session_state.game_data['xp'])
    st.metric("Research Points", st.session_state.game_data['rp'])

st.title("🏛️ Hungerford Holdings: MD Dashboard")

tabs = st.tabs(["⚡ Daily Ops", "💼 Isio/Capital", "🤝 M&A (Dating)", "👴 Stakeholders", "📊 Analytics"])

# TAB 1: DAILY OPS
with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        st.write("### Operational Readiness")
        if st.button("🧘 Meditation (10m)"): update_stat('xp', 15)
        if st.button("🤸 Stretching (15m)"): update_stat('xp', 15)
        if st.button("📖 Industry Reading (30m)"): update_stat('xp', 35)
    with c2:
        st.write("### Property Maintenance")
        if st.button("🧺 Laundry/Housework"): update_stat('xp', 20)
        if st.button("🍽️ Kitchen Clean"): update_stat('xp', 25)

# TAB 2: ISIO & CAPITAL PROJECTS
with tabs[1]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Isio Pursuit Management")
        if st.button("🚀 High-Intensity Bid Work"): update_stat('rp', 100)
        if st.button("🌙 Late Night Strategy Session"): update_stat('rp', 50)
    with col2:
        st.subheader("Legal & Credit (CCJ)")
        if st.button("⚖️ CCJ: Evidence Gathering"): update_stat('xp', 150, is_urgent=True)

# TAB 3: M&A (DATING)
with tabs[2]:
    st.info("Goal: Long-term Strategic Partnership")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔍 Market Research (Dating Apps/Profiles)"): update_stat('xp', 30)
        if st.button("🥂 First Round Interview (Date)"): update_stat('xp', 100)
    with c2:
        if st.button("📍 Out-of-Area Venture (Date outside Harrow)"): update_stat('xp', 150)

# TAB 4: STAKEHOLDERS (DAD & FRIENDS)
with tabs[3]:
    st.subheader("Family Equity (Dad)")
    if st.button("🚗 CR-V Research/Logistics"): update_stat('xp', 50)
    if st.button("📞 Quality Check-in Call"): update_stat('xp', 40)
    
    st.subheader("Social Network")
    if st.button("🍻 Local Catch-up (Harrow)"): update_stat('social_rep', 30)
    if st.button("🚇 Expansion Catch-up (London/Beyond)"): update_stat('social_rep', 75)

# TAB 5: ANALYTICS
with tabs[4]:
    st.write("XP Growth History")
    # (Same logic as v2.4 for chart)
