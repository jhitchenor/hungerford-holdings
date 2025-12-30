import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. DATA LOADING ---
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

if 'game_data' not in st.session_state:
    st.session_state.game_data = load_game_data()

def save_game_data(data):
    try:
        sheet1 = get_gsheet("Sheet1")
        if sheet1:
            sheet1.update('B2:E2', [[data['xp'], data['rp'], data['streak'], data['level']]])
            # Try to log history if sheet exists
            try:
                history_sheet = get_gsheet("XP_History")
                history_sheet.append_row([str(date.today()), data['xp']])
            except: pass
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
    "Chief of Staff": {"img": "assets/cos.png", "title": "Strategic Oversight", "directive": "Jack, darling, we need that CCJ cleared. It's the primary anchor holding the ship back."},
    "Diary Secretary": {"img": "assets/diary.png", "title": "Operations", "directive": "The Harrow HQ needs a reset. I've scheduled your maintenance for this evening."},
    "Head of M&A": {"img": "assets/m_and_a.png", "title": "Growth & Partnerships", "directive": "Harrow is safe, but high-growth acquisitions happen in the West End. Let's expand."},
    "Portfolio Manager": {"img": "assets/portfolio.png", "title": "Finance & Treasury", "directive": "The numbers don't lie. Update the budget tracker today for total clarity."},
    "Performance Coach": {"img": "assets/coach.png", "title": "Human Capital", "directive": "Let's go, Champ! Give me 15 minutes of stretching to unlock that golf power!"}
}

# --- 4. TASK LIBRARIES ---
# Grouped by tab for easier rendering
DATA_DAILY = [
    {"name": "Skincare Routine", "xp": 10, "adv": "Chief of Staff", "msg": "Maintain the brand, Jack. Looking the part is half the battle."},
    {"name": "Supplement Stack", "xp": 10, "adv": "Performance Coach", "msg": "Fuel your brain, Champ! High-octane petrol for your mind!"},
    {"name": "15 mins stretching", "xp": 15, "adv": "Performance Coach", "msg": "Let's get that T-spine rotation back for the fairway!"},
    {"name": "Practice the Perfect Putt ⛳", "xp": 15, "adv": "Performance Coach", "msg": "20 reps. Golf is won on the green."},
    {"name": "Read for 30 mins", "xp": 25, "adv": "Chief of Staff", "msg": "Deep literacy is a competitive advantage. Focus, darling."},
]

DATA_MAINT = [
    {"name": "Laundry Cycle", "xp": 20, "adv": "Diary Secretary", "msg": "Keep the backlog at zero."},
    {"name": "Clean the Kitchen", "xp": 25, "adv": "Diary Secretary", "msg": "The engine room of the home must be spotless."},
    {"name": "Clean the Lounge", "xp": 25, "adv": "Diary Secretary", "msg": "Reset the environment for relaxation."},
    {"name": "Clean the Bathroom", "xp": 30, "adv": "Diary Secretary", "msg": "High-standard hygiene maintenance."},
    {"name": "Remove Shower Mould", "xp": 40, "adv": "Diary Secretary", "msg": "Small fixes prevent structural decay."}
]

DATA_CAPITAL = [
    {"name": "Update budget tracker", "xp": 50, "adv": "Portfolio Manager", "msg": "Liquidity is the foundation of freedom."},
    {"name": "Plan next week's meals", "xp": 50, "adv": "Performance Coach", "msg": "Fuel planning prevents poor performance."},
    {"name": "Reorganise Bedroom", "xp": 80, "adv": "Diary Secretary", "msg": "Your bedroom is your recovery suite."},
    {"name": "Deep work on CCJ project", "xp": 100, "adv": "Chief of Staff", "msg": "Focus, Jack. 90 minutes of flow will slay this beast."},
    {"name": "Review investment portfolio", "xp": 150, "adv": "Portfolio Manager", "msg": "Ensuring the Holdings remain inflation-proof."},
    {"name": "CCJ: Evidence/Filing", "xp": 200, "urgent": True, "adv": "Portfolio Manager", "msg": "This is a priority one audit."}
]

DATA_ISIO = [
    {"name": "Gov/Client Research", "xp": 40, "adv": "Chief of Staff", "msg": "Information is the primary currency of a bid manager."},
    {"name": "Night Owl Session (>8pm)", "rp": 50, "adv": "Diary Secretary", "msg": "I've logged your overtime. Get ahead of the curve."},
    {"name": "Bid/Pursuit Sprint", "rp": 100, "adv": "Chief of Staff", "msg": "Isio's growth depends on this pursuit. Deliver excellence."}
]

DATA_MA = [
    {"name": "Active Networking (Apps)", "xp": 30, "adv": "Head of M&A", "msg": "Don't be shy, handsome. Keep the pipeline full."},
    {"name": "Style & Grooming", "xp": 40, "adv": "Head of M&A", "msg": "Packaging is 50% of the sale."},
    {"name": "Try a new recipe", "xp": 50, "adv": "Performance Coach", "msg": "Surprise your future merger with something bold!"},
    {"name": "The Date (First Round)", "xp": 100, "adv": "Head of M&A", "msg": "Initial due diligence. Assess her values."},
    {"name": "Central London Venture", "xp": 150, "adv": "Head of M&A", "msg": "Expand your territory. The Harrow border is just the beginning."}
]

DATA_STAKE = [
    {"name": "Arsenal Match Engagement", "xp": 25, "adv": "Diary Secretary", "msg": "Morale is a vital metric. Enjoy the game!"},
    {"name": "Weekly Wellness Call (Dad)", "xp": 40, "adv": "Chief of Staff", "msg": "His stability is the foundation of the family office."},
    {"name": "Car Pre-Flight Check", "xp": 40, "adv": "Diary Secretary", "msg": "The CR-V must be mission-ready."},
    {"name": "Book Wedding Hotel", "xp": 50, "urgent": True, "adv": "Diary Secretary", "msg": "Secure the lodging before the market closes."},
    {"name": "Non-Local Catch-up", "xp": 75, "adv": "Head of M&A", "msg": "Maintain those distal connections."},
    {"name": "Visit Hungerford", "xp": 150, "adv": "Chief of Staff", "msg": "Presence is the highest-value investment."}
]

# --- 5. RENDERER ---
def show_tasks(task_list, key_group):
    for i, t in enumerate(task_list):
        c1, c2 = st.columns([0.8, 0.2])
        # Detect if it's an RP task or XP task
        val = t.get('xp') if 'xp' in t else t.get('rp')
        unit = "XP" if 'xp' in t else "RP"
        stat_to_up = 'xp' if 'xp' in t else 'rp'
        
        with c1:
            if st.button(f"{t['name']} (+{val} {unit})", key=f"{key_group}_{i}", use_container_width=True):
                update_stat(stat_to_up, val, is_urgent=t.get('urgent', False))
        with c2:
            with st.popover("🗨️"):
                adv_name = t['adv']
                st.image(ADVISORS[adv_name]['img'], use_container_width=True)
                st.write(f"**{adv_name}**")
                st.write(f"_{t['msg']}_")

# --- 6. UI ---
with st.sidebar:
    try: st.image(ADVISORS["Chief of Staff"]["img"])
    except: st.warning("CoS Image Missing")
    
    st.title(f"Level {st.session_state.game_data['level']}")
    titles = ["Junior Associate", "Senior Analyst", "Associate Director", "Partner", "Managing Director", "Chairman"]
    t_idx = min(st.session_state.game_data['level'] - 1, len(titles)-1)
    st.subheader(titles[t_idx])
    
    # Progress Bar
    xp = st.session_state.game_data['xp']
    nxt = st.session_state.game_data['level'] * 500
    prv = (st.session_state.game_data['level'] - 1) * 500
    p_bar = min(max((xp - prv) / (nxt - prv), 0.0), 1.0)
    st.progress(p_bar)
    st.caption(f"{xp} / {nxt} XP to Next Rank")
    
    st.divider()
    st.metric("Corporate XP", xp)
    st.metric("Isio R&D (RP)", st.session_state.game_data['rp'])
    if st.button("🔥 Log Daily Streak"): update_stat('streak', 1)

st.title("🏛️ Hungerford Holdings: MD Command Center")

tabs = st.tabs(["🏛️ Boardroom", "🚨 Critical Path", "⚡ Daily Ops", "🧹 Maintenance", "💼 Isio & Capital", "🥂 M&A", "👴 Stakeholders"])

with tabs[0]:
    st.markdown("## 👥 Executive Committee Briefing")
    cols = st.columns(5)
    for i, (name, info) in enumerate(ADVISORS.items()):
        with cols[i]:
            try: st.image(info['img'], use_container_width=True)
            except: st.write("[Image]")
            st.caption(f"**{name}**")
            st.info(info['directive'])

with tabs[1]:
    st.error("### 🚨 Urgent Strategic Priorities")
    # Pull tasks marked urgent or high XP
    urgent_pool = [t for t in DATA_CAPITAL + DATA_STAKE if t.get('urgent') or t.get('xp', 0) >= 150]
    show_tasks(urgent_pool, "crit")

with tabs[2]:
    st.subheader("⚡ Operational Readiness")
    show_tasks(DATA_DAILY, "daily")

with tabs[3]:
    st.subheader("🧹 Maintenance & Upkeep")
    show_tasks(DATA_MAINT, "maint")

with tabs[4]:
    st.subheader("💼 Isio Pursuit & Capital Projects")
    show_tasks(DATA_ISIO + DATA_CAPITAL, "isio_cap")

with tabs[5]:
    st.subheader("🥂 M&A (Partnerships)")
    show_tasks(DATA_MA, "ma")

with tabs[6]:
    st.subheader("👴 Stakeholder Relations")
    show_tasks(DATA_STAKE, "stake")
