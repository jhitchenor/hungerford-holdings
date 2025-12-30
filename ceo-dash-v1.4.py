import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. DATA PERSISTENCE ---
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
    except:
        return None, None

def load_data():
    sheet1, task_sheet = get_sheets()
    try:
        row = sheet1.row_values(2)
        # B=XP, C=RP, D=Streak, E=Level, F=Credits, G=Affinity, H=Golf_Best, I=Chase, J=Santander
        stats = {
            "xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]), 
            "level": int(row[4]), "credits": int(row[5]), "affinity": int(row[6]), 
            "golf_best": int(row[7]), "chase_bal": float(row[8]) if len(row) > 8 else 0.0,
            "santander_bal": float(row[9]) if len(row) > 9 else 0.0
        }
    except:
        stats = {"xp": 505, "rp": 0, "streak": 0, "level": 2, "credits": 50, "affinity": 50, "golf_best": 95, "chase_bal": 0.0, "santander_bal": 0.0}
    try: completed = task_sheet.get_all_records()
    except: completed = []
    return stats, completed

if 'game_data' not in st.session_state:
    stats, completed = load_data()
    st.session_state.game_data = stats
    st.session_state.history = completed
    st.session_state.briefing_target = None

def update_permanent(stat_updates, task_id):
    sheet1, task_sheet = get_sheets()
    for stat, amount in stat_updates.items():
        st.session_state.game_data[stat] += amount
        if stat == 'xp': st.session_state.game_data['credits'] += int(amount * 0.1)
        if stat == 'rp': st.session_state.game_data['credits'] += int(amount * 0.2)
    
    today_str = str(date.today())
    task_sheet.append_row([today_str, task_id])
    g = st.session_state.game_data
    sheet1.update('B2:J2', [[g['xp'], g['rp'], g['streak'], g['level'], g['credits'], g['affinity'], g['golf_best'], g['chase_bal'], g['santander_bal']]])
    st.rerun()

# --- 3. TASK LIBRARIES ---

# OPS (XP Focused)
DATA_DAILY = [
    {"id": "skin_d", "name": "Skincare Routine", "xp": 10},
    {"id": "supp_d", "name": "Supplement Stack", "xp": 10},
    {"id": "stretch_d", "name": "Pre-Golf Mobility", "xp": 15},
    {"id": "read_d", "name": "Read for 30 mins", "xp": 20}
]

# MAINTENANCE (XP Focused)
DATA_MAINTENANCE = [
    {"id": "kitchen_d", "name": "Clean Kitchen", "xp": 25},
    {"id": "lounge_d", "name": "Clean Lounge", "xp": 25},
    {"id": "iron_p", "name": "Iron 5 Work Shirts", "xp": 40},
    {"id": "mould_p", "name": "Remove Shower Mould", "xp": 50},
    {"id": "clothes_p", "name": "Bedroom Audit: Dispose Old Clothes", "xp": 80},
    {"id": "bedroom_p", "name": "Bedroom Reorganisation", "xp": 60}
]

# FINANCE (The New Sector)
DATA_FINANCE = [
    {"id": "ccj_p", "name": "CCJ Readiness Check (Jan 2 Strike)", "xp": 50, "urgent": True},
    {"id": "santander_p", "name": "Santander DD Audit", "xp": 60, "urgent": True},
    {"id": "budget_d", "name": "Update Budget Tracker", "xp": 30}
]

# ISIO PURSUIT & TAYLOR (RP Focused)
DATA_ISIO = [
    {"id": "snib_p", "name": "SNIB (9 Jan): Executive Summary", "rp": 120, "xp": 5},
    {"id": "yw_p", "name": "YW (23 Jan): Compliance Review", "rp": 80, "xp": 0},
    {"id": "c4_p", "name": "C4 (14 Jan): Pitch Deck Prep", "rp": 100, "xp": 10},
    {"id": "taylor_gov_p", "name": "Taylor: CDO/CTO Governance Map", "rp": 200, "xp": 25},
    {"id": "taylor_sync_p", "name": "Taylor: Douglas Sync", "rp": 80, "xp": 5},
    {"id": "indesign_p", "name": "InDesign License Request", "rp": 50, "xp": 10},
    {"id": "cmgr_p", "name": "Chartered Manager Pitch (Louise)", "rp": 250, "xp": 100},
]

# M&A (XP Focus)
DATA_MA = [
    {"id": "hinge_p", "name": "Visual Asset Audit (10 Photos)", "xp": 100},
    {"id": "apps_d", "name": "Active Networking (Apps)", "xp": 30},
    {"id": "jacq_p", "name": "Jacqueline (CMO) Briefing", "xp": 40, "rp": 100},
]

# STAKEHOLDERS
DATA_STAKEHOLDERS = [
    {"id": "hotel_p", "name": "Book Wedding Hotel (Krishan)", "xp": 50, "urgent": True},
    {"id": "dad_p", "name": "Wellness Call (Dad)", "xp": 40},
    {"id": "arsenal_d", "name": "Arsenal Match Engagement", "xp": 25},
]

# --- 4. RENDERER ---
def render_command_list(task_list, grp):
    today = str(date.today())
    completed_ids = [r['TaskID'] for r in st.session_state.history]
    for t in task_list:
        t_id = t['id']
        is_done_ever = t_id in completed_ids
        is_done_today = any(r['TaskID'] == t_id and r['Date'] == today for r in st.session_state.history)
        if t_id.endswith("_p") and is_done_ever: continue
        done = is_done_today if t_id.endswith("_d") else is_done_ever
        
        c1, c2 = st.columns([0.85, 0.15])
        with c1:
            xp_val, rp_val = t.get('xp', 0), t.get('rp', 0)
            lbl = f"✅ {t['name']}" if done else f"{t['name']} (+{xp_val} XP / +{rp_val} RP)"
            if st.button(lbl, key=f"btn_{t_id}_{grp}", use_container_width=True, disabled=done):
                update_permanent({'xp': xp_val, 'rp': rp_val}, t_id)
        with c2:
            if st.button("💬", key=f"c_{t_id}_{grp}", use_container_width=True):
                st.session_state.briefing_target = t_id
                st.rerun()
        if st.session_state.briefing_target == t_id:
            with st.container(border=True):
                st.info(t.get('msg', "Advisor monitoring active."))

# --- 5. UI SIDEBAR ---
with st.sidebar:
    st.title("🎖️ Command Dashboard")
    xp, rp = st.session_state.game_data['xp'], st.session_state.game_data['rp']
    
    # XP PROGRESS (Life)
    titles = [(0, "Junior Associate"), (1000, "Senior Analyst"), (2500, "Associate Director"), (5000, "Managing Director")]
    rank = next(title for threshold, title in reversed(titles) if xp >= threshold)
    st.subheader(f"Life Rank: {rank}")
    st.progress(min((xp % 1000) / 1000, 1.0))
    st.caption(f"XP: {xp:,} / 1000 to Next Milestones")
    
    # RP PROGRESS (Career)
    career_titles = [(0, "Grade C"), (1500, "Grade B"), (3000, "Grade A (Principal)"), (5000, "Director Standing")]
    c_rank = next(title for threshold, title in reversed(career_titles) if rp >= threshold)
    st.subheader(f"Career Standing: {c_rank}")
    st.progress(min((rp % 1500) / 1500, 1.0))
    st.caption(f"RP: {rp:,} / 1500 to Next Standing")
    
    st.metric("Treasury Credits", f"💎 {st.session_state.game_data['credits']}")

# --- 6. MAIN UI ---
st.title("🏛️ Hungerford Holdings Command")
tabs = st.tabs(["🏛️ Board", "🚨 Critical", "📈 Finance", "⚡ Ops", "🧹 Maintenance", "💼 Isio Pursuit", "🧪 Taylor Lab", "🥂 M&A", "👴 Stakeholders"])

with tabs[0]: # Boardroom
    cols = st.columns(5)
    directives = [
        ("Chief of Staff", "SNIB Jan 9 is the wall. London HQ proximity to Jacqueline is your advantage."),
        ("Diary Secretary", "Wedding Hotel booking is non-negotiable for tonight. Logistics first."),
        ("Head of M&A", "Get candid golf shots tomorrow. We need to refresh the Hinge asset pool."),
        ("Portfolio Manager", "The CCJ strike on Jan 2nd will unlock significant life equity. Be ready."),
        ("Performance Coach", "40 XP Base for golf + bonus for sub-100. Fight for every stroke!")
    ]
    for i, (name, text) in enumerate(directives):
        with cols[i]:
            st.caption(f"**{name}**")
            st.info(text)

with tabs[1]: # Critical Path
    st.error("### 🚨 Urgent Master Objectives")
    all_t = DATA_DAILY + DATA_MAINTENANCE + DATA_FINANCE + DATA_ISIO + DATA_MA + DATA_STAKEHOLDERS
    crit = [t for t in all_t if t.get('urgent') or t.get('xp', 0) >= 100 or t.get('rp', 0) >= 150]
    render_command_list(crit, "crit")

with tabs[2]: # Finance
    st.header("📈 The Sovereign Treasury")
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Debt & Liquidity Management")
        render_command_list(DATA_FINANCE, "fin")
    with col_r:
        st.subheader("Ledger Sync")
        chase = st.number_input("Chase Balance (£)", value=st.session_state.game_data['chase_bal'])
        sant = st.number_input("Santander Balance (£)", value=st.session_state.game_data['santander_bal'])
        if st.button("Sync Ledger"):
            st.session_state.game_data['chase_bal'], st.session_state.game_data['santander_bal'] = chase, sant
            update_permanent({}, "ledger_sync")

with tabs[4]: render_command_list(DATA_MAINTENANCE, "maint")
with tabs[5]: render_command_list([t for t in DATA_ISIO if "taylor" not in t['id']], "isio")
with tabs[6]: render_command_list([t for t in DATA_ISIO if "taylor" in t['id']], "taylor")

with tabs[8]: # Stakeholders & Golf
    st.header("👴 Stakeholder Management")
    col_g, col_s = st.columns([0.6, 0.4])
    with col_g:
        st.subheader("⛳ Hertsmere Performance Center")
        if "golf_d" not in [r['TaskID'] for r in st.session_state.history if r['Date'] == str(date.today())]:
            score = st.number_input("Enter Score:", 70, 120, 95)
            total_xp = 40 + max(0, 100 - score)
            if st.button(f"Log Round: {score} (+{total_xp} XP)"):
                update_permanent({'xp': total_xp}, "golf_d")
                st.session_state.game_data['golf_best'] = min(score, st.session_state.game_data['golf_best'])
        else: st.success(f"✅ Round Logged. PB: {st.session_state.game_data['golf_best']}")
    with col_s:
        render_command_list(DATA_STAKEHOLDERS, "stake")

with tabs[3]: render_command_list(DATA_DAILY, "daily")
with tabs[7]: render_command_list(DATA_MA, "ma")
