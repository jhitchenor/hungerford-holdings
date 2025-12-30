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
        data = {
            "xp": int(row[1]), 
            "rp": int(row[2]), 
            "streak": int(row[3]), 
            "social_rep": int(row[4]), 
            "level": int(row[5])
        }
        # Start at Level 2 if XP permits
        if data["xp"] >= 500 and data["level"] == 1:
            data["level"] = 2
        return data
    except:
        return {"xp": 505, "rp": 0, "streak": 0, "social_rep": 0, "level": 2}

def save_game_data(data):
    try:
        sheet1 = get_gsheet("Sheet1")
        sheet1.update('B2:F2', [[data['xp'], data['rp'], data['streak'], data['social_rep'], data['level']]])
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
    
    xp_needed_for_next = st.session_state.game_data['level'] * 500
    if st.session_state.game_data['xp'] >= xp_needed_for_next:
        st.session_state.game_data['level'] += 1
        st.balloons()
    
    save_game_data(st.session_state.game_data)
    st.rerun()

# --- 3. UI SETUP ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

with st.sidebar:
    st.title(f"🎖️ Level {st.session_state.game_data['level']}")
    titles = ["Junior Associate", "Senior Analyst", "Associate Director", "Partner", "Managing Director", "Chairman"]
    title_idx = min(st.session_state.game_data['level'] - 1, len(titles)-1)
    st.subheader(titles[title_idx])
    
    # Progress Calculation
    current_xp = st.session_state.game_data['xp']
    next_level_xp = st.session_state.game_data['level'] * 500
    prev_level_xp = (st.session_state.game_data['level'] - 1) * 500
    progress_perc = min(max((current_xp - prev_level_xp) / (next_level_xp - prev_level_xp), 0.0), 1.0)
    
    st.write("Promotion Progress")
    st.progress(progress_perc)
    st.caption(f"{current_xp} / {next_level_xp} XP to next level")
    
    st.divider()
    st.metric("Corporate XP", st.session_state.game_data['xp'])
    st.metric("R&D Points (RP)", st.session_state.game_data['rp'])
    st.metric("Social Rep", st.session_state.game_data['social_rep'])
    if st.button("🔥 Log Streak"): update_stat('streak', 1)

st.title("🏛️ Hungerford Holdings: Strategic Operations")

tabs = st.tabs(["⚡ Daily Ops", "💼 Capital Projects", "🥂 M&A", "👴 Stakeholders", "📊 Treasury"])

# TAB 1: DAILY OPS (Hygiene, Habits, Home)
with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🧘 Operational Readiness")
        if st.button("Meditation (10m)"): update_stat('xp', 15)
        if st.button("Stretching (15m)"): update_stat('xp', 15)
        if st.button("Reading (30m)"): update_stat('xp', 35)
        if st.button("Practice Putting ⛳"): update_stat('xp', 15)
    with c2:
        st.markdown("### 🧹 Property Maintenance")
        if st.button("Laundry Cycle"): update_stat('xp', 20)
        if st.button("Kitchen/Lounge Reset"): update_stat('xp', 25)
        if st.button("Clean Bathroom"): update_stat('xp', 25)
        if st.button("Remove Shower Mould"): update_stat('xp', 40)

# TAB 2: CAPITAL PROJECTS (Isio, Finance, Home Reno)
with tabs[1]:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write("**Isio Pursuit Management**")
        if st.button("High-Intensity Bid Work"): update_stat('rp', 100)
        if st.button("Night Owl Session (>8pm)"): update_stat('rp', 50)
        if st.button("Gov/Client Research"): update_stat('rp', 40)
    with c2:
        st.write("**Financial & Legal**")
        if st.button("Update Budget Tracker"): update_stat('xp', 50)
        if st.button("Review Portfolio"): update_stat('xp', 100)
        if st.button("CCJ: Evidence/Filing"): update_stat('xp', 200, is_urgent=True)
    with c3:
        st.write("**Home Renovation**")
        if st.button("Reorganise Bedroom"): update_stat('xp', 80)
        if st.button("Re-do the Lounge"): update_stat('xp', 100)

# TAB 3: M&A (Dating & Lifestyle)
with tabs[2]:
    st.info("Goal: Long-term Strategic Partnership")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Market Sourcing**")
        if st.button("Apps/Networking"): update_stat('xp', 30)
        if st.button("The Date (First Round)"): update_stat('xp', 100)
        if st.button("Grooming/Style"): update_stat('xp', 40)
    with c2:
        st.write("**Innovation & Health**")
        if st.button("Try a New Recipe"): update_stat('xp', 50)
        if st.button("Meal Planning"): update_stat('xp', 50)
        if st.button("Central London Venture"): update_stat('xp', 150)

# TAB 4: STAKEHOLDERS (Dad & Social)
with tabs[3]:
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Family Equity (Dad)**")
        if st.button("CR-V Market Search"): update_stat('xp', 40)
        if st.button("Car Pre-Flight Check"): update_stat('xp', 40)
        if st.button("Visit Hungerford"): update_stat('xp', 150)
        if st.button("Wellness Call"): update_stat('xp', 40)
    with c2:
        st.write("**Social Capital**")
        if st.button("Book Wedding Hotel"): update_stat('social_rep', 50, is_urgent=True)
        if st.button("Harrow Catch-up"): update_stat('social_rep', 30)
        if st.button("Arsenal Match Day"): update_stat('social_rep', 25)
        if st.button("Non-Local Catch-up"): update_stat('social_rep', 75)

# TAB 5: TREASURY (Analytics)
with tabs[4]:
    st.subheader("Holdings Growth Trend")
    # Charts... (Existing logic)
