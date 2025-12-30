import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. DATA PERSISTENCE & MIGRATION ---
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
    except Exception as e:
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
    """
    stat_updates: dict of {stat_name: amount}
    """
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

# --- 3. ADVISOR PROFILES ---
ADVISORS = {
    "Chief of Staff": {"img": "assets/cos.png", "directive": "Jack, focusing on RP via Taylor AI is the fastest route to Associate Director. Louise's leave in Feb is your window."},
    "Diary Secretary": {"img": "assets/diary.png", "directive": "HQ Reset: Clear the mould and the old clothes. A cluttered environment is a cluttered bid strategy."},
    "Head of M&A": {"img": "assets/m_and_a.png", "directive": "Hertsmere networking with Shivam is key. Get those photos for the Hinge audit tomorrow evening."},
    "Portfolio Manager": {"img": "assets/portfolio.png", "directive": "The Santander account is a legacy risk. Audit the Direct Debits tonight and prepare for liquidation."},
    "Performance Coach": {"img": "assets/coach.png", "directive": "Golf Formula: 40 XP Base. Every stroke under 100 adds 1 XP. Focus on the Pendulum Putt!"}
}

# --- 4. COMPREHENSIVE TASK LIBRARIES ---

# OPS (XP Focus)
DATA_DAILY = [
    {"id": "skin_d", "name": "Skincare Routine", "xp": 10},
    {"id": "supp_d", "name": "Supplement Stack", "xp": 10},
    {"id": "stretch_d", "name": "Pre-Golf Mobility", "xp": 15},
    {"id": "read_d", "name": "Read for 30 mins", "xp": 20},
    {"id": "putt_d", "name": "Putting Practice (20 reps)", "xp": 15}
]

# MAINTENANCE (XP Focus)
DATA_MAINTENANCE = [
    {"id": "kitchen_d", "name": "Clean Kitchen", "xp": 25},
    {"id": "lounge_d", "name": "Clean Lounge", "xp": 25},
    {"id": "iron_p", "name": "Iron 5 Work Shirts", "xp": 40},
    {"id": "mould_p", "name": "Remove Shower Mould", "xp": 50, "msg": "Clear the environmental debt."},
    {"id": "clothes_p", "name": "Bedroom Audit: Dispose Old Clothes", "xp": 80, "msg": "Phase 1 of Reorganisation."},
    {"id": "bedroom_p", "name": "Bedroom Reorganisation", "xp": 60, "msg": "Phase 2: Optimized recovery suite."}
]

# ISIO PURSUIT & TAYLOR (RP Focus)
DATA_ISIO = [
    {"id": "snib_p", "name": "SNIB (9 Jan): Executive Summary", "rp": 120, "xp": 10},
    {"id": "yw_p", "name": "YW (23 Jan): Compliance Review", "rp": 80, "xp": 5},
    {"id": "c4_p", "name": "C4 (14 Jan): Pitch Deck Prep", "rp": 100, "xp": 15},
    {"id": "taylor_gov_p", "name": "Taylor: CDO/CTO Governance Map", "rp": 200, "xp": 30},
    {"id": "taylor_sync_p", "name": "Taylor: Douglas (Edinburgh) Sync", "rp": 80, "xp": 10},
    {"id": "indesign_p", "name": "InDesign License Request", "rp": 50, "xp": 10},
    {"id": "cmgr_p", "name": "Chartered Manager Pitch (Louise)", "rp": 250, "xp": 100},
]

# M&A & STAKEHOLDERS (XP Focus)
DATA_MA = [
    {"id": "hinge_p", "name": "Hinge Visual Asset Audit (10 Photos)", "xp": 100},
    {"id": "apps_d", "name": "Active Networking (Apps)", "xp": 30},
    {"id": "jacq_p", "name": "Jacqueline (CMO) Networking Brief", "xp": 40, "rp": 100},
]

DATA_STAKEHOLDERS = [
    {"id": "hotel_p", "name": "Book Wedding Hotel (Krishan)", "xp": 50, "urgent": True},
    {"id": "dad_p", "name": "Wellness Call (Dad)", "xp": 40},
    {"id": "arsenal_d", "name": "Arsenal Match Engagement", "xp": 25},
]

# --- 5. RENDERER ---
def render_command_list(task_list, grp):
    today = str(date.today())
    completed_ids = [r['TaskID'] for r in st.session_state.history]
    
    for t in task_list:
        t_id = t['id']
        # Permanence logic
        is_done_ever = t_id in completed_ids
        is_done_today = any(r['TaskID'] == t_id and r['Date'] == today for r in st.session_state.history)
        
        if t_id.endswith("_p") and is_done_ever: continue
        done = is_done_today if t_id.endswith("_d") else is_done_ever
        
        c1, c2 = st.columns([0.85, 0.15])
        with c1:
            # Stats string for button
            stat_lbl = ""
            if 'xp' in t: stat_lbl += f"+{t['xp']} XP "
            if 'rp' in t: stat_lbl += f"+{t['rp']} RP"
            
            lbl = f"✅ {t['name']}" if done else f"{t['name']} ({stat_lbl})"
            if st.button(lbl, key=f"btn_{t_id}_{grp}", use_container_width=True, disabled=done):
                updates = {}
                if 'xp' in t: updates['xp'] = t['xp']
                if 'rp' in t: updates['rp'] = t['rp']
                update_permanent(updates, t_id)
        with c2:
            if st.button("💬", key=f"c_{t_id}_{grp}", use_container_width=True):
                st.session_state.briefing_target = t_id
                st.rerun()
        if st.session_state.briefing_target == t_id:
            with st.container(border=True):
                st.info(t.get('msg', "Advisors monitoring active."))

# --- 6. MAIN UI ---
with st.sidebar:
    st.title(f"Level {st.session_state.game_data['level']}")
    xp = st.session_state.game_data['xp']
    titles = [(0, "Junior Associate"), (1000, "Senior Analyst"), (2500, "Associate Director"), (5000, "Managing Director")]
    rank = next(title for threshold, title in reversed(titles) if xp >= threshold)
    st.subheader(rank)
    
    st.metric("Life XP", f"{xp:,}")
    st.metric("Career RP", f"{st.session_state.game_data['rp']:,}")
    st.metric("Credits", f"💎 {st.session_state.game_data['credits']}")
    st.divider()
    st.write("Relationship Affinity")
    st.progress(st.session_state.game_data['affinity'] / 100)

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
    st.error("### 🚨 Master Objectives")
    all_t = DATA_DAILY + DATA_MAINTENANCE + DATA_ISIO + DATA_MA + DATA_STAKEHOLDERS
    crit = [t for t in all_t if t.get('urgent') or t.get('xp', 0) >= 100 or t.get('rp', 0) >= 150]
    render_command_list(crit, "crit")

with tabs[4]: # Pursuit
    st.header("💼 Isio Pursuit Pipeline")
    render_command_list(DATA_ISIO, "isio")

with tabs[8]: # Stakeholders & Finance
    st.header("👴 Stakeholder Management & Finance")
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("⛳ Hertsmere Performance Center")
        if "golf_d" not in [r['TaskID'] for r in st.session_state.history if r['Date'] == str(date.today())]:
            score = st.number_input("Enter Score for Round with Shivam:", 70, 120, 95)
            # THE CORRECTED GOLF LOGIC
            bonus = max(0, 100 - score)
            total_xp = 40 + bonus
            if st.button(f"Log Round: {score} (+{total_xp} XP)"):
                update_permanent({'xp': total_xp}, "golf_d")
                st.session_state.game_data['golf_best'] = min(score, st.session_state.game_data['golf_best'])
        else: st.success(f"✅ Hertsmere Round Logged. Best: {st.session_state.game_data['golf_best']}")
    
    with col_r:
        st.subheader("💰 The Treasury Ledger")
        

[Image of a personal finance dashboard]

        chase = st.number_input("Chase Balance (£):", value=st.session_state.game_data['chase_bal'])
        sant = st.number_input("Santander Balance (£):", value=st.session_state.game_data['santander_bal'])
        if st.button("Update Treasury Ledger"):
            st.session_state.game_data['chase_bal'] = chase
            st.session_state.game_data['santander_bal'] = sant
            update_permanent({}, "ledger_sync") # Just to trigger a save
    
    render_command_list(DATA_STAKEHOLDERS, "stake")

with tabs[2]: render_command_list(DATA_DAILY, "daily")
with tabs[3]: render_command_list(DATA_MAINTENANCE, "maint")
with tabs[5]: render_command_list([t for t in DATA_ISIO if "taylor" in t['id']], "taylor")
with tabs[6]: render_command_list([t for t in DATA_ISIO if "cmgr" in t['id'] or "indesign" in t['id']], "growth")
with tabs[7]: render_command_list(DATA_MA, "ma")
