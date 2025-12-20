import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. GOOGLE SHEETS ENGINE ---
def get_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Check for secrets (Cloud) or local file
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        # Fix for private key newline characters in TOML
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # Fallback for local testing - ensure your json file is in the same folder!
        creds = ServiceAccountCredentials.from_json_keyfile_name("your_key_file.json", scope)
        
    client = gspread.authorize(creds)
    # Ensure this matches your Google Sheet name EXACTLY
    return client.open("Hungerford_Holdings_Data").sheet1

def load_game_data():
    try:
        sheet = get_gsheet()
        row = sheet.row_values(2)
        return {
            "xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]),
            "social_rep": int(row[4]), "level": int(row[5])
        }
    except Exception as e:
        st.error(f"Sync Error: Ensure the Sheet is shared with your service account email!")
        return {"xp": 0, "rp": 0, "streak": 0, "social_rep": 0, "level": 1}

def save_game_data(data):
    sheet = get_gsheet()
    sheet.update('B2:F2', [[data['xp'], data['rp'], data['streak'], data['social_rep'], data['level']]])

# --- 2. INITIALIZATION ---
if 'game_data' not in st.session_state:
    st.session_state.game_data = load_game_data()

def update_stat(stat, amount, is_urgent=False):
    multiplier = 1.5 if is_urgent else 1.0
    final_amount = int(amount * multiplier)
    st.session_state.game_data[stat] += final_amount
    
    # Leveling Logic
    new_level = (st.session_state.game_data['xp'] // 500) + 1
    if new_level > st.session_state.game_data['level']:
        st.session_state.game_data['level'] = new_level
        st.balloons()
        
    save_game_data(st.session_state.game_data)
    st.toast(f"📈 {stat.upper()} +{final_amount} (Cloud Saved)")

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Hungerford Holdings CEO", layout="wide")

st.title(f"🎖️ CEO Level {st.session_state.game_data['level']}")
xp_progress = (st.session_state.game_data['xp'] % 500) / 500
st.progress(min(xp_progress, 1.0))
st.caption(f"XP: {st.session_state.game_data['xp']} | RP: {st.session_state.game_data['rp']}")

t1, t2, t3, t4, t5 = st.tabs(["Daily", "Work/Finance", "Dad", "Social", "Leisure"])

with t1:
    if st.button("✅ Fitness Stack"): update_stat('xp', 20)
    if st.button("🧹 Clean Flat (URGENT)"): update_stat('xp', 50, is_urgent=True)

with t2:
    if st.button("🚀 Project Taylor Sprint"): update_stat('rp', 60)
    if st.button("💰 Finance Review (ISA/Crypto)"): update_stat('rp', 40)

with t3:
    st.info("🎯 Objective: Support Dad & Build Confidence")
    if st.button("🚗 Car Research / Showroom"): update_stat('xp', 50)
    if st.button("🩺 Doctor's Appt Success"): update_stat('xp', 100)
    if st.button("🎿 2026/Skiing Research"): update_stat('xp', 30)

with t4:
    if st.button("🏨 Book Wedding Hotel (URGENT)"): update_stat('social_rep', 40, is_urgent=True)
    if st.button("🏇 Organize Poker/Go-Karting"): update_stat('social_rep', 50)
    if st.button("💬 Reply to Sarah/Neil/Friends"): update_stat('social_rep', 10)

with t5:
    if st.button("📖 Read Economist"): update_stat('xp', 20)
    if st.button("🐎 Watch Slow Horses"): update_stat('xp', 10)
    if st.button("⚽ Sunday Football"): update_stat('xp', 40)
