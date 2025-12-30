import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. PERMANENCE ENGINE ---
def get_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("your_key_file.json", scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key("1wZSAKq283Q1xf9FAeMBIw403lpavRRAVLKNntc950Og")
        return spreadsheet.worksheet("Sheet1"), spreadsheet.worksheet("Completed_Tasks")
    except: return None, None

def load_data():
    sheet1, task_sheet = get_sheets()
    try:
        row = sheet1.row_values(2)
        stats = {"xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]), "level": int(row[4]), 
                 "credits": int(row[5]), "affinity": int(row[6]), "golf_best": int(row[7])}
    except:
        stats = {"xp": 505, "rp": 0, "streak": 0, "level": 2, "credits": 50, "affinity": 50, "golf_best": 95}
    try: completed = task_sheet.get_all_records()
    except: completed = []
    return stats, completed

if 'game_data' not in st.session_state:
    stats, completed = load_data()
    st.session_state.game_data = stats
    st.session_state.history = completed
    st.session_state.briefing_target = None

def update_stat_permanent(stat, amount, task_id):
    sheet1, task_sheet = get_sheets()
    st.session_state.game_data[stat] += amount
    if stat == 'xp': st.session_state.game_data['credits'] += int(amount * 0.1)
    if stat == 'rp': st.session_state.game_data['credits'] += int(amount * 0.2)
    
    today_str = str(date.today())
    task_sheet.append_row([today_str, task_id])
    g = st.session_state.game_data
    sheet1.update('B2:H2', [[g['xp'], g['rp'], g['streak'], g['level'], g['credits'], g['affinity'], g['golf_best']]])
    st.rerun()

# --- 3. ADVISOR PROFILES ---
ADVISORS = {
    "Chief of Staff": {"img": "assets/cos.png", "directive": "Jack, Louise leaves in Feb. The 'CMgr' pitch is your play for HQ influence with Jacqueline and Matt W."},
    "Diary Secretary": {"img": "assets/diary.png", "directive": "Operational hygiene: Clear the mould and the old clothes tonight. We start 2026 with an optimized environment."},
    "Head of M&A": {"img": "assets/m_and_a.png", "directive": "Hertsmere candid shots are high-value assets for Hinge. Focus on the green, handsome."},
    "Portfolio Manager": {"img": "assets/portfolio.png", "directive": "Taylor Governance is non-negotiable for Matt G and Vito. We need a technical roadmap."},
    "Performance Coach": {"img": "assets/coach.png", "directive": "Football was Phase 1. Golf is Phase 2. Focus on the $100 - strokes$ efficiency bonus!"}
}

# --- 4. THE COMPREHENSIVE TASK AUDIT ---

# TAB: DAILY OPS
DATA_DAILY = [
    {"id": "skin_d", "name": "Skincare Routine", "xp": 10, "adv": "Chief of Staff"},
    {"id": "supp_d", "name": "Supplement Stack", "xp": 10, "adv": "Performance Coach"},
    {"id": "stretch_d", "name": "Pre-Golf T-Spine Mobility", "xp": 15, "adv": "Performance Coach"},
    {"id": "read_d", "name": "Read for 30 mins", "xp": 20, "adv": "Chief of Staff"},
    {"id": "putting_d", "name": "Practice Putting (20 Reps)", "xp": 15, "adv": "Performance Coach"},
]

# TAB: MAINTENANCE
DATA_MAINTENANCE = [
    {"id": "kitchen_d", "name": "Clean Kitchen", "xp": 25, "adv": "Diary Secretary"},
    {"id": "lounge_d", "name": "Clean Lounge", "xp": 25, "adv": "Diary Secretary"},
    {"id": "iron_p", "name": "Iron 5 Work Shirts (Fri Readiness)", "xp": 40, "adv": "Diary Secretary"},
    {"id": "mould_p", "name": "Remove Shower Mould", "xp": 50, "adv": "Diary Secretary"},
    {"id": "clothes_p", "name": "Bedroom Audit: Throw Out Old Clothes", "xp": 80, "adv": "Diary Secretary"},
    {"id": "bedroom_p", "name": "Bedroom Reorganisation", "xp": 60, "adv": "Diary Secretary"},
]

# TAB: ISIO PURSUIT (RP Focus)
DATA_ISIO_RP = [
    {"id": "snib_p", "name": "SNIB (9 Jan): Executive Summary Draft", "rp": 120, "xp": 15, "adv": "Chief of Staff"},
    {"id": "yw_p", "name": "Yorkshire Water (23 Jan): Technical Compliance", "rp": 80, "xp": 10, "adv": "Portfolio Manager"},
    {"id": "c4_p", "name": "Channel 4 (14 Jan): Presentation Deck", "rp": 100, "xp": 20, "adv": "Performance Coach"},
    {"id": "snib_pitch_p", "name": "SNIB (15 Jan): Pitch Architecture", "rp": 100, "xp": 20, "adv": "Chief of Staff"},
    {"id": "hs2_p", "name": "HS2: Multi-Service Line Prospecting", "rp": 50, "xp": 10, "adv": "Chief of Staff"},
]

# TAB: TAYLOR LAB
DATA_TAYLOR = [
    {"id": "taylor_gov_p", "name": "Taylor: Governance Strategy (Vito/Matt G)", "rp": 200, "xp": 40, "adv": "Portfolio Manager"},
    {"id": "taylor_sync_p", "name": "Taylor: Logic Sync with Douglas", "rp": 80, "xp": 10, "adv": "Chief of Staff"},
]

# TAB: GROWTH
DATA_GROWTH = [
    {"id": "cmgr_p", "name": "Pitch CMgr Qualification to Louise", "rp": 250, "xp": 100, "adv": "Chief of Staff"},
    {"id": "indesign_p", "name": "Acquire InDesign License", "rp": 50, "xp": 20, "adv": "Diary Secretary"},
    {"id": "jacq_p", "name": "Networking Briefing: Jacqueline (CMO)", "rp": 120, "xp": 40, "adv": "Head of M&A"},
]

# TAB: M&A (Social/Dating)
DATA_MA = [
    {"id": "hinge_p", "name": "Visual Asset Audit: 10 Hinge Photos", "xp": 100, "adv": "Head of M&A"},
    {"id": "networking_d", "name": "Active Networking (Apps)", "xp": 30, "adv": "Head of M&A"},
    {"id": "grooming_d", "name": "Style & Grooming Maintenance", "xp": 20, "adv": "Head of M&A"},
]

# TAB: STAKEHOLDERS & FINANCE
DATA_STAKEHOLDERS = [
    {"id": "hotel_p", "name": "Book Wedding Hotel (Krishan)", "xp": 50, "urgent": True, "adv": "Diary Secretary"},
    {"id": "dad_p", "name": "Wellness Call (Dad)", "xp": 40, "adv": "Chief of Staff"},
    {"id": "arsenal_d", "name": "Arsenal Match Engagement", "xp": 25, "adv": "Diary Secretary"},
]

DATA_CAPITAL = [
    {"id": "ccj_p", "name": "CCJ Readiness Check (Jan 2 Strike)", "xp": 50, "adv": "Portfolio Manager"},
    {"id": "santander_p", "name": "Santander DD Audit", "xp": 60, "adv": "Portfolio Manager"},
    {"id": "budget_d", "name": "Update Budget Tracker", "xp": 30, "adv": "Portfolio Manager"},
]

# --- 5. RENDERER ---
def render_command_list(task_list, grp):
    today = str(date.today())
    completed_ids = [r['TaskID'] for r in st.session_state.history]
    for t in task_list:
        t_id = t['id']
        is_in_sheet = t_id in completed_ids
        was_done_today = any(r['TaskID'] == t_id and r['Date'] == today for r in st.session_state.history)
        if t_id.endswith("_p") and is_in_sheet: continue
        done = was_done_today if t_id.endswith("_d") else is_in_sheet
        c1, c2 = st.columns([0.85, 0.15])
        with c1:
            lbl = f"✅ {t['name']}" if done else f"{t['name']} (+{t.get('xp',0)} XP / +{t.get('rp',0)} RP)"
            if st.button(lbl, key=f"btn_{t_id}_{grp}", use_container_width=True, disabled=done):
                if 'xp' in t: update_stat_permanent('xp', t['xp'], t_id)
                if 'rp' in t: update_stat_permanent('rp', t['rp'], t_id)
        with c2:
            if st.button("💬", key=f"c_{t_id}_{grp}", use_container_width=True):
                st.session_state.briefing_target = t_id
                st.rerun()
        if st.session_state.briefing_target == t_id:
            with st.container(border=True):
                st.info(t.get('msg', "Advisor monitoring active."))

# --- 6. UI ---
with st.sidebar:
    st.title(f"Level {st.session_state.game_data['level']}")
    xp_total = st.session_state.game_data['xp']
    st.subheader("MD Command Center")
    st.metric("Life XP", f"{xp_total:,}")
    st.metric("Career RP", f"{st.session_state.game_data['rp']:,}")
    st.metric("Credits", f"💎 {st.session_state.game_data['credits']}")

st.title("🏛️ Hungerford Holdings Command")
tabs = st.tabs(["🏛️ Board", "🚨 Critical", "⚡ Ops", "🧹 Maintenance", "💼 Isio Pursuit", "🧪 Taylor Lab", "🥂 Growth", "🥂 M&A", "👴 Stakeholders"])

with tabs[0]: # Boardroom
    cols = st.columns(5)
    for i, (name, info) in enumerate(ADVISORS.items()):
        with cols[i]:
            st.image(info['img'], use_container_width=True)
            st.caption(f"**{name}**")
            st.info(info['directive'])

with tabs[1]: # Critical Path
    st.error("### 🚨 Urgent Master Objectives")
    all_tasks = DATA_DAILY + DATA_MAINTENANCE + DATA_ISIO_RP + DATA_TAYLOR + DATA_GROWTH + DATA_MA + DATA_STAKEHOLDERS + DATA_CAPITAL
    crit = [t for t in all_tasks if t.get('urgent') or t.get('xp', 0) >= 100 or t.get('rp', 0) >= 150]
    render_command_list(crit, "crit")

with tabs[2]: render_command_list(DATA_DAILY, "daily")
with tabs[3]: render_command_list(DATA_MAINTENANCE, "maint")
with tabs[4]: 
    st.header("💼 Isio Pursuit: EB Portfolio")
    
    render_command_list(DATA_ISIO_RP, "isio")
with tabs[5]: 
    st.header("🧪 Taylor AI: Strategic R&D")
    

[Image of a software development life cycle]

    render_command_list(DATA_TAYLOR, "taylor")
with tabs[6]: render_command_list(DATA_GROWTH, "growth")
with tabs[7]: render_command_list(DATA_MA, "ma")
with tabs[8]: 
    st.header("👴 Stakeholder Management")
    render_command_list(DATA_STAKEHOLDERS + DATA_CAPITAL, "stake")
    st.divider()
    st.subheader("⛳ Hertsmere Performance Center")
    
    if "golf_d" not in [r['TaskID'] for r in st.session_state.history if r['Date'] == str(date.today())]:
        score = st.number_input("Enter Score for Round with Shivam:", 70, 120, 95)
        bonus = max(0, 100 - score)
        total_xp = 40 + bonus
        if st.button(f"Log Round: {score} (+{total_xp} XP)"):
            update_stat_permanent('xp', total_xp, "golf_d")
            st.session_state.game_data['golf_best'] = min(score, st.session_state.game_data['golf_best'])
    else: st.success(f"✅ Hertsmere Round Logged. Best: {st.session_state.game_data['golf_best']}")
