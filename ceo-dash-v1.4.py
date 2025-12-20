import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, datetime

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
        return {
            "xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]),
            "social_rep": int(row[4]), "level": int(row[5])
        }
    except:
        return {"xp": 0, "rp": 0, "streak": 0, "social_rep": 0, "level": 1}

def save_game_data(data):
    # Update Main Stats
    sheet1 = get_gsheet("Sheet1")
    sheet1.update('B2:F2', [[data['xp'], data['rp'], data['streak'], data['social_rep'], data['level']]])
    
    # Log History for Graphing
    try:
        history_sheet = get_gsheet("XP_History")
        today_str = str(date.today())
        # Append as a new row: [Date, Total_XP]
        history_sheet.append_row([today_str, data['xp']])
    except:
        pass # If user hasn't created the tab yet, don't crash

# --- 2. INITIALIZATION ---
if 'game_data' not in st.session_state:
    st.session_state.game_data = load_game_data()

def update_stat(stat, amount, is_urgent=False):
    multiplier = 1.5 if is_urgent else 1.0
    final_amount = int(amount * multiplier)
    st.session_state.game_data[stat] += final_amount
    save_game_data(st.session_state.game_data)
    st.toast(f"📈 {stat.upper()} +{final_amount}")

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Hungerford Holdings CEO", layout="wide")

st.title(f"🎖️ CEO Level {st.session_state.game_data['level']}")
st.progress(min((st.session_state.game_data['xp'] % 500) / 500, 1.0))

tabs = st.tabs(["📅 Roadmap", "📊 Progress Analytics", "⚡ Ops", "🚀 Work", "💰 Finance", "🤝 Dad"])

# TAB: ROADMAP (Previously built)
with tabs[0]:
    st.header("🗓️ Weekly Outlook")
    st.write("Check your upcoming deadlines and car prep here.")

# --- NEW TAB: ANALYTICS ---
with tabs[1]:
    st.header("📈 Historical Success Tracking")
    try:
        history_sheet = get_gsheet("XP_History")
        df = pd.DataFrame(history_sheet.get_all_records())
        
        if not df.empty:
            # Group by date and get the max XP for each day
            df['Date'] = pd.to_datetime(df['Date'])
            daily_max = df.groupby('Date')['Total_XP'].max().reset_index()
            
            # Calculate Daily Earned (Difference between days)
            daily_max['Daily_Earned'] = daily_max['Total_XP'].diff().fillna(daily_max['Total_XP'])
            
            st.subheader("Total XP Progression")
            st.line_chart(daily_max.set_index('Date')['Total_XP'])
            
            st.subheader("Daily Productivity (XP Earned per Day)")
            st.bar_chart(daily_max.set_index('Date')['Daily_Earned'])
        else:
            st.info("Log your first task to start generating your success graph!")
    except:
        st.warning("To enable graphs, please add a tab named 'XP_History' to your Google Sheet.")

# (Keep your existing Ops, Work, Finance, and Dad buttons here...)
with tabs[2]:
    if st.button("✅ Fitness Stack"): update_stat('xp', 30)
    if st.button("🧹 Clean Flat (URGENT)"): update_stat('xp', 50, is_urgent=True)
    if st.button("🚗 Car Pre-Flight: Oil & Air"): update_stat('xp', 40)

with tabs[3]:
    if st.button("🤖 Taylor: Governance"): update_stat('rp', 70)

with tabs[4]:
    if st.button("⚖️ CCJ Boss Battle"): update_stat('xp', 150, is_urgent=True)

with tabs[5]:
    if st.button("🚗 Car Research / Showroom"): update_stat('xp', 50)
    if st.button("🏌️ Driving Range Session"): update_stat('xp', 30)
