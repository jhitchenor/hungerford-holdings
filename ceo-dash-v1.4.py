import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- GOOGLE SHEETS CONNECTION ---
def get_gsheet():
    # In Streamlit Cloud, we put the JSON content in "Secrets"
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Check if we are local or in the cloud
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # Locally, it looks for your downloaded JSON
        creds = ServiceAccountCredentials.from_json_keyfile_name("your_key_file.json", scope)
        
    client = gspread.authorize(creds)
    return client.open("Hungerford_Holdings_Data").sheet1

def load_data():
    sheet = get_gsheet()
    row = sheet.row_values(2) # Gets our stats from row 2
    return {
        "xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]),
        "social_rep": int(row[4]), "level": int(row[5])
    }

def save_data(data):
    sheet = get_gsheet()
    # Update row 2 with new values
    sheet.update('B2:F2', [[data['xp'], data['rp'], data['streak'], data['social_rep'], data['level']]])

# --- INITIALIZE GAME ---
if 'game_data' not in st.session_state:
    st.session_state.game_data = load_data()

def update_stat(stat, amount, is_urgent=False):
    multiplier = 1.5 if is_urgent else 1.0
    final_amount = int(amount * multiplier)
    st.session_state.game_data[stat] += final_amount
    
    # Level Up Logic
    new_level = (st.session_state.game_data['xp'] // 500) + 1
    if new_level > st.session_state.game_data['level']:
        st.session_state.game_data['level'] = new_level
        st.balloons()
        
    save_data(st.session_state.game_data)
    st.toast(f"📈 {stat.upper()} +{final_amount} (Saved to Cloud!)")

# --- UI (Simplified for phone) ---
st.set_page_config(page_title="Hungerford Holdings CEO", layout="wide")

st.title(f"🎖️ CEO Level {st.session_state.game_data['level']}")
st.progress(min((st.session_state.game_data['xp'] % 500) / 500, 1.0))

t1, t2, t3, t4 = st.tabs(["Daily", "Work", "Dad", "Social"])

with t1:
    if st.button("✅ Fitness Stack"): update_stat('xp', 20)
    if st.button("🧹 Clean Flat"): update_stat('xp', 50, is_urgent=True)

with t2:
    if st.button("🚀 Project Taylor"): update_stat('rp', 60)
    if st.button("💰 Finance Review"): update_stat('rp', 40)

with t3:
    st.info("🎯 Goal: Boost Dad's Confidence")
    if st.button("🚗 Car Showroom Visit"): update_stat('xp', 50)
    if st.button("🩺 Doctor's Appointment"): update_stat('xp', 100)
    if st.button("🎿 Skiing Research"): update_stat('xp', 30)

with t4:
    if st.button("🏨 Book Wedding Hotel"): update_stat('social_rep', 40, is_urgent=True)
    if st.button("🏇 Poker/Go-Karting"): update_stat('social_rep', 50)
