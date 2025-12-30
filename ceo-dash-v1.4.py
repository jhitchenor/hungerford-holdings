import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. SET PAGE CONFIG (Must be the very first Streamlit command) ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. GOOGLE SHEETS ENGINE ---
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
    except Exception as e:
        st.error(f"Sheet Connection Error: {e}")
        return None

def load_game_data():
    """Forces a return of a valid dictionary even if the sheet fails."""
    default_data = {"xp": 505, "rp": 0, "streak": 0, "level": 2}
    try:
        sheet = get_gsheet("Sheet1")
        if sheet:
            row = sheet.row_values(2)
            # B:XP, C:RP, D:Streak, E:Level
            data = {
                "xp": int(row[1]), 
                "rp": int(row[2]), 
                "streak": int(row[3]), 
                "level": int(row[4])
            }
            if data["xp"] >= 500 and data["level"] == 1:
                data["level"] = 2
            return data
        return default_data
    except:
        return default_data

# --- 3. INITIALIZE SESSION STATE (The Fix) ---
if 'game_data' not in st.session_state:
    st.session_state.game_data = load_game_data()

# --- 4. CORE FUNCTIONS ---
def save_game_data(data):
    try:
        sheet1 = get_gsheet("Sheet1")
        if sheet1:
            sheet1.update('B2:E2', [[data['xp'], data['rp'], data['streak'], data['level']]])
            history_sheet = get_gsheet("XP_History")
            history_sheet.append_row([str(date.today()), data['xp']])
    except:
        pass

def update_stat(stat, amount, is_urgent=False):
    multiplier = 1.5 if is_urgent else 1.0
    final_amount = int(amount * multiplier)
    st.session_state.game_data[stat] += final_amount
    
    # Level Up Logic
    xp_needed = st.session_state.game_data['level'] * 500
    if st.session_state.game_data['xp'] >= xp_needed:
        st.session_state.game_data['level'] += 1
        st.balloons()
    
    save_game_data(st.session_state.game_data)
    st.rerun()

# --- 5. ADVISOR & TASK DATA ---
ADVISOR_DATA = {
    "Chief of Staff": {"img": "assets/cos.png", "title": "Executive Office"},
    "Diary Secretary": {"img": "assets/diary.png", "title": "Operations"},
    "Head of M&A": {"img": "assets/m_and_a.png", "title": "Growth & Partnerships"},
    "Portfolio Manager": {"img": "assets/portfolio.png", "title": "Finance & Treasury"},
    "Performance Coach": {"img": "assets/coach.png", "title": "Human Capital"}
}

def render_task_section(task_list, key_prefix, is_rp=False):
    sorted_tasks = sorted(task_list, key=lambda x: x['xp'])
    for t in sorted_tasks:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            stat_label = "RP" if is_rp else "XP"
            if st.button(f"{t['name']} (+{t['xp']} {stat_label})", key=f"{key_prefix}_{t['name']}", use_container_width=True):
                update_stat('rp' if is_rp else 'xp', t['xp'], is_urgent=t.get('urgent', False))
        with col2:
            if "advisor" in t:
                with st.popover("ℹ️"):
                    adv = t['advisor']
                    if adv in ADVISOR_DATA:
                        st.image(ADVISOR_DATA[adv]['img'], use_container_width=True)
                    st.caption(f"Memo from {adv}")
                    st.markdown(f"*{t['advice']}*")

# Task Libraries
daily_ops = [
    {"name": "Skincare Routine", "xp": 10, "advisor": "Chief of Staff", "advice": "Standard operational procedure. Maintain the 'Executive Image'."},
    {"name": "Supplement Stack", "xp": 10, "advisor": "Performance Coach", "advice": "Vitamin D, Omega-3, and Magnesium. Support the nervous system."},
    {"name": "15 mins stretching", "xp": 15, "advisor": "Performance Coach", "advice": "Focus on T-spine rotations for your golf swing."},
    {"name": "Practice the Perfect Putt ⛳", "xp": 15, "advisor": "Performance Coach", "advice": "20 reps for muscle memory."},
    {"name": "Read for 30 mins", "xp": 25, "advisor": "Chief of Staff", "advice": "Deep literacy is a competitive advantage."},
]

house_maint = [
    {"name": "Laundry Cycle", "xp": 20, "advisor": "Diary Secretary", "advice": "Keep the 'Branch Office' (Harrow HQ) in order."},
    {"name": "Clean the Kitchen", "xp": 25, "advisor": "Diary Secretary", "advice": "A clean kitchen is the foundation of home health."},
    {"name": "Clean the Lounge", "xp": 25, "advisor": "Diary Secretary", "advice": "Reset the environment for relaxation."},
    {"name": "Clean the Bathroom", "xp": 30, "advisor": "Diary Secretary", "advice": "High-standard hygiene maintenance."},
    {"name": "Remove Shower Mould", "xp": 40, "advisor": "Diary Secretary", "advice": "Small fixes prevent long-term 'Structural Decay'."},
]

capital_isio = [
    {"name": "Update budget tracker", "xp": 50, "advisor": "Portfolio Manager", "advice": "Liquidity is king, Jack."},
    {"name": "Plan next week's meals", "xp": 50, "advisor": "Performance Coach", "advice": "Fuel planning prevents poor performance."},
    {"name": "Reorganise Bedroom", "xp": 80, "advisor": "Diary Secretary", "advice": "Sleep hygiene starts with an organized space."},
    {"name": "Deep work on CCJ project", "xp": 100, "advisor": "Chief of Staff", "advice": "Concentrated effort to remove this liability."},
    {"name": "Review investment portfolio", "xp": 150, "advisor": "Portfolio Manager", "advice": "Rebalance assets for long-term growth."},
    {"name": "CCJ: Evidence/Filing", "xp": 200, "urgent": True, "advisor": "Portfolio Manager", "advice": "Finalizing the legal audit. Priority one."},
]

isio_performance = [
    {"name": "Bid/Pursuit Sprint", "xp": 100, "advisor": "Chief of Staff", "advice": "Isio's growth depends on this pursuit."},
    {"name": "Night Owl Session (>8pm)", "xp": 50, "advisor": "Diary Secretary", "advice": "Leveraging late-night productivity."}
]

m_a_dating = [
    {"name": "Active Networking (Apps)", "xp": 30, "advisor": "Head of M&A", "advice": "Treat it like lead generation."},
    {"name": "Style & Grooming", "xp": 40, "advisor": "Head of M&A", "advice": "Packaging is 50% of the sale."},
    {"name": "Try a new recipe", "xp": 50, "advisor": "Performance Coach", "advice": "A high-ROI skill for future domestic partnership."},
    {"name": "The Date (First Round)", "xp": 100, "advisor": "Head of M&A", "advice": "Initial due diligence. Assess values."},
    {"name": "Central London Venture", "xp": 150, "advisor": "Head of M&A", "advice": "Break the Harrow bubble."}
]

stakeholders = [
    {"name": "Arsenal Match Engagement", "xp": 25, "advisor": "Diary Secretary", "advice": "Maintaining morale and social standing."},
    {"name": "Weekly Wellness Call (Dad)", "xp": 40, "advisor": "Chief of Staff", "advice": "His stability is your stability."},
    {"name": "Car Pre-Flight Check", "xp": 40, "advisor": "Diary Secretary", "advice": "Ensure transport readiness."},
    {"name": "Book Wedding Hotel", "xp": 50, "urgent": True, "advisor": "Diary Secretary", "advice": "Social reputation is on the line."},
    {"name": "Non-Local Catch-up", "xp": 75, "advisor": "Head of M&A", "advice": "Diversify your social portfolio."},
    {"name": "Visit Hungerford", "xp": 150, "advisor": "Chief of Staff", "advice": "Direct oversight of the family wellbeing."}
]

# --- 6. UI RENDER ---

# Sidebar
with st.sidebar:
    try:
        st.image(ADVISOR_DATA["Chief of Staff"]["img"])
    except:
        st.warning("CoS Image not found in /assets")
        
    st.title(f"🎖️ Level {st.session_state.game_data['level']}")
    titles = ["Junior Associate", "Senior Analyst", "Associate Director", "Partner", "Managing Director", "Chairman"]
    title_idx = min(st.session_state.game_data['level'] - 1, len(titles)-1)
    st.subheader(titles[title_idx])
    
    # Progress Bar
    curr = st.session_state.game_data['xp']
    nxt = st.session_state.game_data['level'] * 500
    prv = (st.session_state.game_data['level'] - 1) * 500
    prog = min(max((curr - prv) / (nxt - prv), 0.0), 1.0)
    st.progress(prog)
    st.caption(f"{curr} / {nxt} XP to next Promotion")
    
    st.divider()
    st.metric("Corporate XP", st.session_state.game_data['xp'])
    st.metric("R&D Points (RP)", st.session_state.game_data['rp'])

st.title("🏛️ Hungerford Holdings: Strategic Operations")

tabs = st.tabs(["🏛️ Boardroom", "🚨 Critical Path", "⚡ Daily Ops", "🧹 Maintenance", "💼 Capital & Isio", "🥂 M&A", "👴 Stakeholders"])

with tabs[0]:
    st.markdown("## 👥 Executive Committee Briefing")
    cols = st.columns(5)
    for i, (name, info) in enumerate(ADVISOR_DATA.items()):
        with cols[i]:
            try:
                st.image(info['img'], use_container_width=True)
            except:
                st.write("[Image Missing]")
            st.caption(f"**{name}**")
            st.write(f"*{info['title']}*")

with tabs[1]:
    st.error("### Memo from the Chief of Staff")
    all_tasks = daily_ops + house_maint + capital_isio + m_a_dating + stakeholders
    urgent_items = [t for t in all_tasks if t.get('urgent') or t['xp'] >= 150]
    render_task_section(urgent_items, "crit")

with tabs[2]:
    render_task_section(daily_ops, "daily")

with tabs[3]:
    render_task_section(house_maint, "maint")

with tabs[4]:
    st.markdown("### 🧪 R&D (Isio Performance)")
    render_task_section(isio_performance, "isio_rp", is_rp=True)
    st.divider()
    st.markdown("### 🚀 Strategic Projects")
    render_task_section(capital_isio, "cap")

with tabs[5]:
    render_task_section(m_a_dating, "ma")

with tabs[6]:
    render_task_section(stakeholders, "stake")
