import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date, timedelta

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
    save_game_data(st.session_state.game_data)
    st.toast(f"📈 {stat.upper()} +{final_amount}")

# --- 3. TEMPORAL LOGIC ---
today = date.today()
day_name = today.strftime("%A")
travel_date = date(2025, 12, 24)
wedding_deadline = date(2025, 12, 23)

# --- 4. UI LAYOUT ---
st.set_page_config(page_title="Hungerford Holdings CEO", layout="wide")

with st.sidebar:
    st.title(f"🎖️ Level {st.session_state.game_data['level']} CEO")
    st.write(f"**Today:** {day_name}, Dec {today.day}")
    st.divider()
    st.metric("Corporate XP", st.session_state.game_data['xp'])
    st.metric("Research Points", st.session_state.game_data['rp'])
    if st.button("Advance Daily Streak"): update_stat('streak', 1)

st.title("🏛️ Hungerford Holdings: Strategic Roadmap")

# --- TABS ---
tabs = st.tabs(["📅 Roadmap", "⚡ Ops & Maint", "🚀 Work/Finance", "🤝 Dad", "📣 Social", "🛀 Recovery"])

# TAB 0: THE NEW CALENDAR VIEW
with tabs[0]:
    st.header("🗓️ Weekly Operational Outlook")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.subheader("Upcoming Events")
        st.write(f"📍 **Dec 23:** Wedding Hotel Deadline")
        st.write(f"🚗 **Dec 24:** Deployment to Hungerford")
        st.write(f"🎂 **Dec 27:** Neil's Birthday")
        st.write(f"🎆 **Jan 01:** New Year IPO")

    with col_b:
        st.subheader("Active Bonuses")
        # Bonus logic for Wedding Hotel
        days_to_wedding_dl = (wedding_deadline - today).days
        if days_to_wedding_dl >= 0:
            st.success(f"🔥 **1.5x Multiplier:** Wedding Hotel Booking (Expires in {days_to_wedding_dl}d)")
        
        # Bonus for Pre-Travel Car Check
        if today < travel_date:
            st.info("🛠️ **Pre-Flight Bonus:** Car Oil & Air Check active until Dec 24.")

    with col_c:
        st.subheader("Recurring Quests")
        if day_name == "Wednesday":
            st.warning("🗑️ **URGENT:** Bin Day! Collection tomorrow morning.")
        else:
            st.write("⚪ Wednesday: Bin Day Prep")
        st.write("⚪ Thursday: FPL Deadline")

# TAB 1: OPS & MAINTENANCE
with tabs[1]:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Fitness Stack"): update_stat('xp', 30)
        if st.button("🧹 Clean Flat (URGENT)"): update_stat('xp', 50, is_urgent=True)
        if st.button("🧺 Laundry Cycle"): update_stat('xp', 10)
    with c2:
        # Pre-Travel Car Task
        if today < travel_date:
            if st.button("🚗 Car Pre-Flight: Oil & Air Pressure"):
                update_stat('xp', 40)
                st.success("Vehicle status: Green. Ready for Hungerford deployment.")
        
        # Bin Day (Only on Wednesday)
        if day_name == "Wednesday":
            if st.button("🗑️ Put Bins Out (Bin Day Quest)"):
                update_stat('xp', 20)
                st.balloons()

# (Keep your existing Work, Finance, Dad, Social, and Recovery tabs below)
with tabs[2]:
    st.write("### R&D and Capital")
    if st.button("🤖 Taylor: Governance"): update_stat('rp', 70)
    if st.button("⚖️ CCJ Boss Battle"): update_stat('xp', 150, is_urgent=True)

with tabs[3]:
    st.write("### Supporting Dad")
    if st.button("🚗 Car Research"): update_stat('xp', 50)
    if st.button("🩺 Doctor's Appt"): update_stat('xp', 100)

with tabs[4]:
    if st.button("🏨 Book Wedding Hotel"): update_stat('social_rep', 40, is_urgent=True)
    if st.button("💬 Reply to Friends"): update_stat('social_rep', 10)

with tabs[5]:
    if st.button("📖 Read Economist"): update_stat('xp', 20)
    if st.button("⚽ Arsenal Game (Social Buff)"): update_stat('xp', 15)
