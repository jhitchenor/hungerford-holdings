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
    save_game_data(st.session_state.game_data)
    st.toast(f"📈 {stat.upper()} +{final_amount}")

# --- 3. TEMPORAL DATA ---
today = date.today()
day_name = today.strftime("%A")
travel_date = date(2025, 12, 24)

# --- 4. UI LAYOUT ---
st.set_page_config(page_title="Hungerford Holdings CEO", layout="wide")

with st.sidebar:
    st.title(f"🎖️ Level {st.session_state.game_data['level']} CEO")
    st.write(f"📅 **{day_name}, Dec {today.day}**")
    st.divider()
    st.metric("Corporate XP", st.session_state.game_data['xp'])
    st.metric("Research Points", st.session_state.game_data['rp'])
    if st.button("Advance Daily Streak"): update_stat('streak', 1)

st.title("🏛️ Hungerford Holdings: Strategic Ops")

tabs = st.tabs(["📅 Roadmap", "📊 Analytics", "⚡ Daily Ops", "🧹 Property Maint.", "🚀 Capital Projects", "🤝 Dad", "📣 Social"])

# TAB 0: ROADMAP
with tabs[0]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Upcoming Targets")
        st.write("📍 **Dec 23:** Hotel Deadline & CCJ Phase 1")
        st.write("🚗 **Dec 24:** Deployment to Hungerford HQ")
        st.write("🎂 **Dec 27:** Neil's Birthday")
    with col2:
        st.subheader("Active Bonuses")
        if today < travel_date: st.info("🛠️ **Car Pre-Flight Check:** Oil & Air Pressure bonus active.")
        if day_name == "Wednesday": st.error("🗑️ **BIN DAY:** Put them out for tomorrow's collection!")

# TAB 1: ANALYTICS (Existing Logic)
with tabs[1]:
    try:
        history_sheet = get_gsheet("XP_History")
        df = pd.DataFrame(history_sheet.get_all_records())
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'])
            daily_max = df.groupby('Date')['Total_XP'].max().reset_index()
            st.line_chart(daily_max.set_index('Date')['Total_XP'])
    except: st.warning("Add 'XP_History' to Google Sheets.")

# TAB 2: DAILY OPS (Hygiene & Habits)
with tabs[2]:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧼 Hygiene Stack (Skincare/Self-Care)"): update_stat('xp', 10)
        if st.button("🏋️ Fitness Stack (Football/Press-ups)"): update_stat('xp', 30)
        if st.button("📖 Quality Journalism (Economist/FT)"): update_stat('xp', 20)
    with c2:
        if st.button("🌳 Spend Time Outside (Walk/Parks)"): update_stat('xp', 15)
        if st.button("⛳ Practice the Perfect Putt"): update_stat('xp', 15)

# TAB 3: PROPERTY MAINTENANCE (Housework)
with tabs[3]:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧺 Complete Laundry Cycle"): update_stat('xp', 10)
        if st.button("🍽️ Clean the Kitchen"): update_stat('xp', 20)
    with c2:
        if st.button("🚿 Clean the Bathroom"): update_stat('xp', 20)
        if day_name == "Wednesday":
            if st.button("🗑️ Put Bins Out"): update_stat('xp', 20)

# TAB 4: CAPITAL PROJECTS (The Big Stuff)
with tabs[4]:
    st.subheader("Isio Work (R&D)")
    if st.button("🤖 Taylor: Governance Protocol"): update_stat('rp', 75)
    
    st.subheader("Financial & Credit Repair")
    if st.button("⚖️ CCJ Boss Battle: ID Creditor"): update_stat('xp', 50)
    if st.button("📑 Complete N443/CCJ Evidence"): update_stat('xp', 150, is_urgent=True)
    
    st.subheader("Home Renovation Projects")
    if st.button("🛏️ Reorganise Bedroom"): update_stat('xp', 80)
    if st.button("🧼 Remove Shower Mould"): update_stat('xp', 40)
    if st.button("🛋️ Re-do the Lounge"): update_stat('xp', 100)

# TAB 5: DAD (CR-V Strategy)
with tabs[5]:
    st.info("Strategy: 5th Gen (2019-2023) Hybrid AWD Focus")
    if st.button("🚗 Car Pre-Flight: Oil & Air"): update_stat('xp', 40)
    if st.button("🔍 Find 3x 5th Gen AWD EX on AutoTrader"): update_stat('xp', 30)

# TAB 6: SOCIAL
with tabs[6]:
    if st.button("🏨 Book Wedding Hotel"): update_stat('social_rep', 40, is_urgent=True)
    if st.button("⚽ Arsenal Game (Social Buff)"): update_stat('xp', 15)
