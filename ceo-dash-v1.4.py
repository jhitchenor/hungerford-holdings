import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. GOOGLE SHEETS ENGINE ---
def get_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("your_key_file.json", scope)
        
    client = gspread.authorize(creds)
    
    # YOUR UNIQUE SPREADSHEET ID
    SPREADSHEET_ID = "1wZSAKq283Q1xf9FAeMBIw403lpavRRAVLKNntc950Og" 
    return client.open_by_key(SPREADSHEET_ID).sheet1

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
    
    # Leveling Logic (500 XP per level)
    new_level = (st.session_state.game_data['xp'] // 500) + 1
    if new_level > st.session_state.game_data['level']:
        st.session_state.game_data['level'] = new_level
        st.balloons()
        st.success(f"🎊 LEVEL UP! You are now a Level {new_level} CEO.")
        
    save_game_data(st.session_state.game_data)
    st.toast(f"📈 {stat.upper()} +{final_amount} (Saved to Cloud)")

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Hungerford Holdings CEO", layout="wide")

# Sidebar Progress
with st.sidebar:
    st.title(f"🎖️ CEO Level {st.session_state.game_data['level']}")
    xp_for_next = st.session_state.game_data['level'] * 500
    current_progress = (st.session_state.game_data['xp'] % 500) / 500
    st.write(f"XP to Level {st.session_state.game_data['level'] + 1}")
    st.progress(min(current_progress, 1.0))
    st.write(f"Streak Multiplier: x{1 + (st.session_state.game_data['streak'] * 0.1):.1f}")
    if st.button("Advance Daily Streak"): update_stat('streak', 1)

st.title("🏛️ Hungerford Holdings: Strategic Dashboard")
st.caption(f"Current Stats | XP: {st.session_state.game_data['xp']} | RP: {st.session_state.game_data['rp']} | Social: {st.session_state.game_data['social_rep']}")

tabs = st.tabs(["⚡ Daily & Maintenance", "🚀 Isio Work (R&D)", "💰 Finances", "🤝 Stakeholder (Dad)", "📣 Social", "🛀 Recovery"])

# T1: Daily Ops
with tabs[0]:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Fitness Stack (Football/Press-ups)"): update_stat('xp', 30)
        if st.button("🧹 Clean Flat (URGENT)"): update_stat('xp', 50, is_urgent=True)
    with col2:
        if st.button("🧺 Washing/Laundry Cycle"): update_stat('xp', 10)
        if st.button("🚿 Skincare & Self-Care"): update_stat('xp', 10)

# T2: Isio Work (R&D)
with tabs[1]:
    st.header("Project Pipeline")
    if st.button("🤖 Taylor: Draft Governance Protocol"): update_stat('rp', 75)
    if st.button("📋 EB Starters: Director-Ready Polish"): update_stat('rp', 60)
    if st.button("🦾 RFP Automation: Prompt Engineering"): update_stat('rp', 50)

# T3: Finances (Capital)
with tabs[2]:
    st.error("BOSS BATTLE: CCJ Resolution")
    if st.button("⚖️ Complete N443/CCJ Evidence (+150 XP)"): update_stat('xp', 150, is_urgent=True)
    st.divider()
    if st.button("📊 ISA/Gold/ETF Rebalance"): update_stat('rp', 40)
    if st.button("₿ Crypto (BTC/ETH) Tactical Move"): update_stat('rp', 30)
    if st.button("📑 IFA Trust Letter of Wishes"): update_stat('xp', 60)

# T4: Stakeholder (Dad)
with tabs[3]:
    st.info("Current Focus: Support & Confidence Building")
    if st.button("🚗 Car Research / Showroom Visit"): update_stat('xp', 50)
    if st.button("🏌️ Driving Range / Golf Prep"): update_stat('xp', 30)
    if st.button("🩺 Secure Doctor's Appt (Soft Nudge)"): update_stat('xp', 100)
    if st.button("🎿 2026 Trip / Skiing Planning"): update_stat('xp', 30)

# T5: Social
with tabs[4]:
    if st.button("🏨 Book Wedding Hotel (URGENT)"): update_stat('social_rep', 40, is_urgent=True)
    if st.button("💬 Reply to Sarah/Neil/Friends"): update_stat('social_rep', 10)
    if st.button("🏇 Organize Poker/Go-Karting"): update_stat('social_rep', 60)

# T6: Recovery
with tabs[5]:
    if st.button("📖 Read Economist Article"): update_stat('xp', 20)
    if st.button("🐎 Watch Slow Horses"): update_stat('xp', 15)
    if st.button("⚽ Saturday Football (Arsenal Game)"): update_stat('xp', 15)
