import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. SET PAGE CONFIG (MUST BE FIRST) ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. GOOGLE SHEETS & DATA PERSISTENCE ---
def get_gsheet(sheet_name="Sheet1"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("your_key_file.json", scope)
        client = gspread.authorize(creds)
        SPREADSHEET_ID = "1wZSAKq283Q1xf9FAeMBIw403lpavRRAVLKNntc950Og" 
        return client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
    except: return None

def load_game_data():
    default_data = {"xp": 505, "rp": 0, "streak": 0, "level": 2}
    try:
        sheet = get_gsheet("Sheet1")
        if sheet:
            row = sheet.row_values(2)
            data = {"xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]), "level": int(row[4])}
            if data["xp"] >= 500 and data["level"] == 1: data["level"] = 2
            return data
        return default_data
    except: return default_data

# Initialize State
if 'game_data' not in st.session_state:
    st.session_state.game_data = load_game_data()

def save_game_data(data):
    try:
        sheet1 = get_gsheet("Sheet1")
        if sheet1:
            sheet1.update('B2:E2', [[data['xp'], data['rp'], data['streak'], data['level']]])
            history_sheet = get_gsheet("XP_History")
            history_sheet.append_row([str(date.today()), data['xp']])
    except: pass

def update_stat(stat, amount, is_urgent=False):
    multiplier = 1.5 if is_urgent else 1.0
    st.session_state.game_data[stat] += int(amount * multiplier)
    xp_needed = st.session_state.game_data['level'] * 500
    if st.session_state.game_data['xp'] >= xp_needed:
        st.session_state.game_data['level'] += 1
        st.balloons()
    save_game_data(st.session_state.game_data)
    st.rerun()

# --- 3. ADVISOR PROFILES ---
ADVISORS = {
    "Chief of Staff": {
        "img": "assets/cos.png",
        "title": "Strategic Oversight",
        "voice": "Authoritative & Warm",
        "directive": "Jack, darling, we need that CCJ cleared. It's the only anchor holding the ship back. Let's make it our primary objective this week."
    },
    "Diary Secretary": {
        "img": "assets/diary.png",
        "title": "Operations",
        "voice": "Crisp & Professional",
        "directive": "Logistics check: The Harrow HQ needs a reset. I've scheduled your maintenance tasks for this evening. No backlog allowed."
    },
    "Head of M&A": {
        "img": "assets/m_and_a.png",
        "title": "Growth & Partnerships",
        "voice": "Flirty & Strategic",
        "directive": "The London market is heating up, handsome. Staying in Harrow is safe, but high-growth acquisitions happen in the West End."
    },
    "Portfolio Manager": {
        "img": "assets/portfolio.png",
        "title": "Finance & Treasury",
        "voice": "Analytical & Precise",
        "directive": "The numbers don't lie. I need that budget tracker updated today so we can forecast your 2026 expansion."
    },
    "Performance Coach": {
        "img": "assets/coach.png",
        "title": "Human Capital",
        "voice": "Bubbly & Energetic",
        "directive": "Let's go, Champ! Your T-spine is looking stiff. Give me 15 minutes of stretching to unlock that golf power!"
    }
}

# --- 4. TASK LIBRARIES ---
daily_ops = [
    {"name": "Skincare Routine", "xp": 10, "advisor": "Chief of Staff", "advice": "We must maintain the brand, Jack. Looking the part is half the battle."},
    {"name": "Supplement Stack", "xp": 10, "advisor": "Performance Coach", "advice": "Fuel your brain, Champ! Those Omega-3s are like high-octane petrol for your mind!"},
    {"name": "15 mins stretching", "xp": 15, "advisor": "Performance Coach", "advice": "Deep breaths! Let's get that T-spine rotation back so you can crush it on the fairway!"},
    {"name": "Practice the Perfect Putt ⛳", "xp": 15, "advisor": "Performance Coach", "advice": "20 reps. Golf is won on the green, not the tee."},
    {"name": "Read for 30 mins", "xp": 25, "advisor": "Chief of Staff", "advice": "Deep literacy is a competitive advantage in bid management. Focus, darling."},
]

house_maint = [
    {"name": "Laundry Cycle", "xp": 20, "advisor": "Diary Secretary", "advice": "A clean uniform for a clean mindset. Keep the backlog at zero."},
    {"name": "Clean the Kitchen", "xp": 25, "advisor": "Diary Secretary", "advice": "The engine room of the home must be spotless."},
    {"name": "Clean the Lounge", "xp": 25, "advisor": "Diary Secretary", "advice": "Optimizing the rest area. You can't perform if your lounge is cluttered."},
    {"name": "Clean the Bathroom", "xp": 30, "advisor": "Diary Secretary", "advice": "Sanitation is a non-negotiable standard for the MD."},
    {"name": "Remove Shower Mould", "xp": 40, "advisor": "Diary Secretary", "advice": "Addressing deferred maintenance now prevents structural decay later."}
]

capital_isio = [
    {"name": "Update budget tracker", "xp": 50, "advisor": "Portfolio Manager", "advice": "Know your numbers, Jack. Liquidity is the foundation of freedom."},
    {"name": "Plan next week's meals", "xp": 50, "advisor": "Performance Coach", "advice": "Fuel planning prevents poor performance. Don't eat like an amateur!"},
    {"name": "Reorganise Bedroom", "xp": 80, "advisor": "Diary Secretary", "advice": "Your bedroom is your recovery suite. Make it worthy of an executive."},
    {"name": "Deep work on CCJ project", "xp": 100, "advisor": "Chief of Staff", "advice": "Focus, Jack. 90 minutes of flow will slay this beast."},
    {"name": "Review investment portfolio", "xp": 150, "advisor": "Portfolio Manager", "advice": "Rebalancing assets to ensure the Holdings remain inflation-proof."},
    {"name": "CCJ: Evidence/Filing", "xp": 200, "urgent": True, "advisor": "Portfolio Manager", "advice": "This is a priority one audit. Ensure every timestamp is recorded."}
]

isio_performance = [
    {"name": "Bid/Pursuit Sprint", "xp": 100, "advisor": "Chief of Staff", "advice": "Isio's growth depends on this pursuit. Deliver excellence, as always."},
    {"name": "Night Owl Session (>8pm)", "xp": 50, "advisor": "Diary Secretary", "advice": "I've logged your overtime. Use this quiet time to get ahead of the curve."},
    {"name": "Gov/Client Research", "xp": 40, "advisor": "Chief of Staff", "advice": "Information is the primary currency of a bid manager."}
]

m_a_dating = [
    {"name": "Active Networking (Apps)", "xp": 30, "advisor": "Head of M&A", "advice": "Don't be shy, handsome. It's a numbers game—keep the pipeline full."},
    {"name": "Style & Grooming", "xp": 40, "advisor": "Head of M&A", "advice": "Packaging is 50% of the sale. I want you looking like a Partner."},
    {"name": "Try a new recipe", "xp": 50, "advisor": "Performance Coach", "advice": "Culinary skill is a top-tier asset. Surprise your future merger with something bold!"},
    {"name": "The Date (First Round)", "xp": 100, "advisor": "Head of M&A", "advice": "Initial due diligence. Assess her values, not just her LinkedIn."},
    {"name": "Central London Venture", "xp": 150, "advisor": "Head of M&A", "advice": "Expanding the search radius. Let's find a spot in Marylebone and show them who you are."}
]

stakeholders = [
    {"name": "Arsenal Match Engagement", "xp": 25, "advisor": "Diary Secretary", "advice": "Morale is a vital metric. Enjoy the game, but stay disciplined."},
    {"name": "Weekly Wellness Call (Dad)", "xp":
