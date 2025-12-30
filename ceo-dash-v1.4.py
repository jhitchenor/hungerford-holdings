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
        # B:XP, C:RP, D:Streak, E:SocialRep, F:Level
        data = {
            "xp": int(row[1]), 
            "rp": int(row[2]), 
            "streak": int(row[3]), 
            "social_rep": int(row[4]), 
            "level": int(row[5])
        }
        
        # MANUAL OVERRIDE: If XP > 500 and still Level 1, promote to Level 2
        if data["xp"] >= 500 and data["level"] == 1:
            data["level"] = 2
            
        return data
    except Exception as e:
        return {"xp": 505, "rp": 0, "streak": 0, "social_rep": 0, "level": 2}

def save_game_data(data):
    try:
        sheet1 = get_gsheet("Sheet1")
        sheet1.update('B2:F2', [[data['xp'], data['rp'], data['streak'], data['social_rep'], data['level']]])
        history_sheet = get_gsheet("XP_History")
        history_sheet.append_row([str(date.today()), data['xp']])
    except:
        pass

# --- 2. INITIALIZATION ---
if 'game_data' not in st.session_state:
    st.session_state.game_data = load_game_data()

def update_stat(stat, amount, is_urgent=False):
    multiplier = 1.5 if is_urgent else 1.0
    final_amount = int(amount * multiplier)
    st.session_state.game_data[stat] += final_amount
    
    # LEVEL UP LOGIC: Level * 500
    xp_needed_for_next = st.session_state.game_data['level'] * 500
    if st.session_state.game_data['xp'] >= xp_needed_for_next:
        st.session_state.game_data['level'] += 1
        st.balloons()
        st.success(f"PROMOTED! You are now a Level {st.session_state.game_data['level']} Executive.")
        
    save_game_data(st.session_state.game_data)
    st.rerun() # Refresh UI to show new stats immediately

# --- 3. UI SETUP ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# Sidebar
with st.sidebar:
    st.title(f"🎖️ Level {st.session_state.game_data['level']}")
    
    titles = ["Junior Associate", "Senior Analyst", "Associate Director", "Partner", "Managing Director", "Chairman"]
    title_idx = min(st.session_state.game_data['level'] - 1, len(titles)-1)
    st.subheader(titles[title_idx])
    
    # Progress Bar
    current_xp = st.session_state.game_data['xp']
    next_level_xp = st.session_state.game_data['level'] * 500
    prev_level_xp = (st.session_state.game_data['level'] - 1) * 500
    
    progress_range = next_level_xp - prev_level_xp
    progress_current = current_xp - prev_level_xp
    progress_perc = min(max(progress_current / progress_range, 0.0), 1.0)
    
    st.write("Promotion Progress")
    st.progress(progress_perc)
    st.caption(f"{current_xp} / {next_level_xp} XP to next level")
    
    st.divider()
    st.metric("Total Corporate XP", st.session_state.game_data['xp'])
    st.metric("R&D Points (RP)", st.session_state.game_data['rp'])
    st.metric("Social Reputation", st.session_state.game_data['social_rep'])
    
    if st.button("🔥 Log Daily Streak"):
        update_stat('streak', 1)

# Main Dashboard
st.title("🏛️ Hungerford Holdings: Strategic Operations")
st.write(f"Welcome back, MD. Today is {date.today().strftime('%A, %d %B')}.")

# Re-defining Tabs to ensure content is captured
tab_titles = ["⚡ Daily Ops", "💼 Isio & Projects", "🥂 M&A (Dating)", "👴 Stakeholders", "📊 Analytics"]
tabs = st.tabs(tab_titles)

with tabs[0]:
    st.markdown("### 🧘 Operational Readiness")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Morning Meditation (10m)", key="med"): update_stat('xp', 15)
        if st.button("Flexibility & Stretching (15m)", key="stretch"): update_stat('xp', 15)
        if st.button("Reading (Financial/Journalism)", key="read"): update_stat('xp', 35)
    with col2:
        if st.button("Nutritional Meal Prep", key="meal"): update_stat('xp', 40)
        if st.button("Laundry Cycle", key="laundry"): update_stat('xp', 20)
        if st.button("Kitchen/Lounge Reset", key="kitchen"): update_stat('xp', 25)

with tabs[1]:
    st.markdown("### 🚀 Isio & Capital Projects")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Isio Pursuit Management**")
        if st.button("High-Intensity Bid/Pursuit Work", key="isio_high"): update_stat('rp', 100)
        if st.button("Night Owl Strategy (After 8pm)", key="isio_late"): update_stat('rp', 50)
    with col2:
        st.write("**Legal & Credit (The CCJ)**")
        if st.button("ID Creditor / Gather Evidence", key="ccj_ev"): update_stat('xp', 150, is_urgent=True)
        if st.button("Submit N443/Legal Filing", key="ccj_file"): update_stat('xp', 250, is_urgent=True)

with tabs[2]:
    st.markdown("### 🥂 M&A (Dating & Growth)")
    st.info("Objective: Secure a long-term strategic partnership.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Active Networking (Apps/Events)", key="date_net"): update_stat('xp', 30)
        if st.button("First Round Interview (The Date)", key="date_first"): update_stat('xp', 100)
    with col2:
        if st.button("Central London Venture (Out of Harrow)", key="date_london"): update_stat('xp', 150)
        if st.button("Personal Presentation (Style/Grooming)", key="groom"): update_stat('xp', 40)
