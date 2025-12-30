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
    # Using your existing Spreadsheet ID
    SPREADSHEET_ID = "1wZSAKq283Q1xf9FAeMBIw403lpavRRAVLKNntc950Og" 
    return client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)

def load_game_data():
    try:
        sheet = get_gsheet("Sheet1")
        row = sheet.row_values(2)
        # B:XP, C:RP, D:Streak, E:SocialRep, F:Level
        return {
            "xp": int(row[1]), 
            "rp": int(row[2]), 
            "streak": int(row[3]), 
            "social_rep": int(row[4]), 
            "level": int(row[5])
        }
    except Exception as e:
        # Fallback if sheet is empty or error occurs
        return {"xp": 0, "rp": 0, "streak": 0, "social_rep": 0, "level": 1}

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
    # Apply urgency multiplier
    multiplier = 1.5 if is_urgent else 1.0
    final_amount = int(amount * multiplier)
    st.session_state.game_data[stat] += final_amount
    
    # LEVEL UP LOGIC
    # Formula: Level 1 needs 500xp, Level 2 needs 1000xp, etc.
    xp_needed_for_next = st.session_state.game_data['level'] * 500
    if st.session_state.game_data['xp'] >= xp_needed_for_next:
        st.session_state.game_data['level'] += 1
        st.balloons()
        st.success(f"PROMOTED! You are now a Level {st.session_state.game_data['level']} Executive.")
        
    save_game_data(st.session_state.game_data)
    st.toast(f"📈 {stat.upper()} +{final_amount}")

# --- 3. UI SETUP ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# Sidebar - The Executive Summary
with st.sidebar:
    st.title(f"🎖️ Level {st.session_state.game_data['level']}")
    
    # Corporate Titles based on Level
    titles = ["Junior Associate", "Senior Analyst", "Associate Director", "Partner", "Managing Director", "Chairman"]
    title_idx = min(st.session_state.game_data['level'] - 1, len(titles)-1)
    st.subheader(titles[title_idx])
    
    # Progress Bar Calculation
    current_xp = st.session_state.game_data['xp']
    next_level_xp = st.session_state.game_data['level'] * 500
    prev_level_xp = (st.session_state.game_data['level'] - 1) * 500
    # Guard against division by zero
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

tabs = st.tabs(["⚡ Daily Ops", "💼 Isio & Projects", "🥂 M&A (Dating)", "👴 Stakeholders", "📊 Analytics"])

# TAB 1: DAILY OPS (Maintenance & Wellness)
with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🧘 Operational Readiness")
        if st.button("Morning Meditation (10m)"): update_stat('xp', 15)
        if st.button("Flexibility & Stretching (15m)"): update_stat('xp', 15)
        if st.button("Reading (Financial/Journalism)"): update_stat('xp', 35)
        if st.button("Nutritional Meal Prep"): update_stat('xp', 40)
    with c2:
        st.markdown("### 🧹 Property Management")
        if st.button("Laundry Cycle"): update_stat('xp', 20)
        if st.button("Kitchen/Lounge Reset"): update_stat('xp', 25)
        if st.button("Bathroom Maintenance"): update_stat('xp', 30)

# TAB 2: ISIO & CAPITAL PROJECTS
with tabs[1]:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🚀 Isio Pursuit Management")
        if st.button("High-Intensity Bid/Pursuit Work"): update_stat('rp', 100)
        if st.button("Night Owl Strategy Session (After 8pm)"): update_stat('rp', 50)
        if st.button("Client Research / Governance"): update_stat('rp', 40)
    with col2:
        st.markdown("### ⚖️ Legal & Credit (The CCJ)")
        st.caption("Critical Path: Clearing the CCJ")
        if st.button("ID Creditor / Gather Evidence"): update_stat('xp', 150, is_urgent=True)
        if st.button("Submit N443/Legal Filing"): update_stat('xp', 250, is_urgent=True)

# TAB 3: M&A (DATING & GROWTH)
with tabs[2]:
    st.info("Strategic Objective: Secure a long-term partnership (Wife).")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🔍 Market Sourcing")
        if st.button("Active Networking (Apps/Events)"): update_stat('xp', 30)
        if st.button("First Round Interview (The Date)"): update_stat('xp', 100)
    with c2:
        st.markdown("### 🗺️ Market Expansion")
        if st.button("Central London Venture (Out of Harrow)"): update_stat('xp', 150)
        if st.button("Personal Presentation (Style/Grooming)"): update_stat('xp', 40)

# TAB 4: STAKEHOLDERS (DAD & FRIENDS)
with tabs[3]:
    st.markdown("### 👴 Family Equity (Dad)")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("CR-V Market Analysis/Logistics"): update_stat('xp', 50)
        if st.button("Quality Visit to Hungerford"): update_stat('xp', 150)
    with c2:
        if st.button("Weekly Wellness Check-in Call"): update_stat('xp', 40)
    
    st
