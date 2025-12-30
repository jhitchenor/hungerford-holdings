import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. THE SOVEREIGN ENGINE ---
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

# --- 3. ADVISOR PROFILES ---
ADVISORS = {
    "Chief of Staff": {"img": "assets/cos.png", "directive": "Jack, Louise's mat-leave is a power vacuum. The CMgr pitch is your claim to HQ leadership."},
    "Diary Secretary": {"img": "assets/diary.png", "directive": "The 'Harrow Reset' (Mould/Clothes) must be finalized tonight to ensure a zero-friction return to Isio."},
    "Head of M&A": {"img": "assets/m_and_a.png", "directive": "Dating is due diligence. Use the Hertsmere round to gather high-value visual assets for Hinge."},
    "Portfolio Manager": {"img": "assets/portfolio.png", "directive": "The CCJ strike on Jan 2nd is our primary audit goal. Ensure liquidity is moved to Chase."},
    "Performance Coach": {"img": "assets/coach.png", "directive": "Football recovery tonight; Golf performance tomorrow. Every stroke under 100 is an XP dividend!"}
}

# --- 4. THE COMPREHENSIVE INTELLIGENCE LEDGER ---

DATA_DAILY = [
    {"id": "skin_d", "name": "Skincare Routine", "xp": 10, "adv": "Chief of Staff", "msg": "Executive presence starts with the face. Standardize the routine."},
    {"id": "supp_d", "name": "Supplement Stack", "xp": 10, "adv": "Performance Coach", "msg": "Post-football recovery: Magnesium, Zinc, and hydration for tomorrow's tee time."},
    {"id": "stretch_d", "name": "Pre-Golf Mobility", "xp": 15, "adv": "Performance Coach", "msg": "Unlock your T-spine. We need that rotation to beat Shivam."},
    {"id": "read_d", "name": "Read for 30 mins", "xp": 20, "adv": "Chief of Staff", "msg": "Broadening the intellectual portfolio. Knowledge is the ultimate leverage."}
]

DATA_MAINTENANCE = [
    {"id": "iron_p", "name": "Iron 5 Work Shirts", "xp": 40, "adv": "Diary Secretary", "msg": "Visual standards for Friday. We don't do 'creased' in the London HQ."},
    {"id": "mould_p", "name": "Remove Shower Mould", "xp": 50, "adv": "Diary Secretary", "msg": "Addressing deferred maintenance. Structural hygiene is a priority."},
    {"id": "clothes_p", "name": "Bedroom Audit: Dispose Old Clothes", "xp": 80, "adv": "Diary Secretary", "msg": "Liquidate the legacy wardrobe. Clear the rack for higher-value assets."},
    {"id": "bedroom_p", "name": "Bedroom Reorganisation", "xp": 60, "adv": "Diary Secretary", "msg": "Phase 2: Optimize the recovery suite for 2026 operations."}
]

DATA_FINANCE = [
    {"id": "ccj_p", "name": "CCJ Readiness Check (Jan 2 Strike)", "xp": 50, "urgent": True, "adv": "Portfolio Manager", "msg": "Priority Alpha. Ensure the creditor is live and the Chase funds are liquid."},
    {"id": "santander_p", "name": "Santander DD Audit", "xp": 60, "urgent": True, "adv": "Portfolio Manager", "msg": "Audit the 'relic' account. Any missed direct debits represent operational leakage."},
    {"id": "budget_d", "name": "Update Budget Tracker", "xp": 30, "adv": "Portfolio Manager", "msg": "Accuracy in the ledger ensures freedom in the splurge."}
]

DATA_ISIO_PURSUITS = [
    {"id": "snib_p", "name": "SNIB (9 Jan): Executive Summary", "rp": 120, "adv": "Chief of Staff", "msg": "Collaborating with Matt W. He needs the London HQ 'polish' on this response."},
    {"id": "yw_p", "name": "YW (23 Jan): Compliance Review", "rp": 80, "adv": "Portfolio Manager", "msg": "Steady-state technical audit. Accuracy is non-negotiable for Yorkshire Water."},
    {"id": "jacq_p", "name": "Jacqueline (CMO) HQ Networking", "rp": 100, "xp": 20, "adv": "Chief of Staff", "msg": "The 'Water Cooler' Gambit. Build equity while your remote colleagues are invisible."},
    {"id": "cmgr_p", "name": "Chartered Manager Pitch (Louise)", "rp": 250, "xp": 50, "adv": "Chief of Staff", "msg": "Louise leaves in Feb. Pitch CMgr as the leadership framework for EB growth."}
]

DATA_ISIO_TAYLOR = [
    {"id": "taylor_gov_p", "name": "Taylor: CDO/CTO Governance Map", "rp": 200, "adv": "Portfolio Manager", "msg": "Appeasement Strategy: Map the logic to satisfy Matt G and Vito's 'organic growth' concerns."},
    {"id": "taylor_sync_p", "name": "Taylor: Douglas Sync", "rp": 80, "adv": "Chief of Staff", "msg": "Synchronizing with Edinburgh. Ensure Douglas is aligned with the HQ roadmap."}
]

DATA_MA = [
    {"id": "hinge_p", "name": "Visual Asset Audit (10 Photos)", "xp": 100, "adv": "Head of M&A", "msg": "Cull the weak assets. Replace with tomorrow's candid golf shots."},
    {"id": "apps_d", "name": "Active Networking (Apps)", "xp": 30, "adv": "Head of M&A", "msg": "Lead generation in the West End sector. Maintain a warm pipeline."},
    {"id": "grooming_d", "name": "Grooming Maintenance", "xp": 20, "adv": "Head of M&A", "msg": "The brand is you. Stay sharp, handsome."}
]

# --- 5. RENDERER ---
def render_command_list(task_list, grp, show_rp=False):
    today = str(date.today())
    completed_ids = [r['TaskID'] for r in st.session_state.history]
    for t in task_list:
        t_id, adv_name = t['id'], t['adv']
        is_done = t_id in completed_ids if t_id.endswith("_p") else any(r['TaskID'] == t_id and r['Date'] == today for r in st.session_state.history)
        if t_id.endswith("_p") and t_id in completed_ids: continue
        
        c1, c2 = st.columns([0.85, 0.15])
        with c1:
            stat_str = f"+{t.get('rp', 0)} RP" if show_rp else f"+{t.get('xp', 0)} XP"
            lbl = f"✅ {t['name']}" if is_done else f"{t['name']} ({stat_str})"
            if st.button(lbl, key=f"btn_{t_id}_{grp}", use_container_width=True, disabled=is_done):
                update_permanent({'xp': t.get('xp', 0), 'rp': t.get('rp', 0)}, t_id)
        with c2:
            if st.button("💬", key=f"c_{t_id}_{grp}", use_container_width=True):
                st.session_state.briefing_target = t_id
                st.rerun()
        if st.session_state.briefing_target == t_id:
            with st.container(border=True):
                col_i, col_t = st.columns([0.2, 0.8])
                with col_i: st.image(ADVISORS[adv_name]['img'], width=100)
                with col_t:
                    st.caption(f"**Briefing from {adv_name}**")
                    st.info(t['msg'])

# --- 6. UI ---
with st.sidebar:
    st.title("🎖️ Command Dashboard")
    xp, rp = st.session_state.game_data['xp'], st.session_state.game_data['rp']
    titles = [(0, "Junior Associate"), (1000, "Senior Analyst"), (2500, "Associate Director"), (5000, "Managing Director")]
    rank = next(title for threshold, title in reversed(titles) if xp >= threshold)
    st.subheader(f"Rank: {rank}")
    st.progress(min((xp % 1000) / 1000, 1.0))
    st.caption(f"XP: {xp:,} / 1000 to Milestone")
    
    st.subheader("Career Standing")
    st.progress(min((rp % 1500) / 1500, 1.0))
    st.caption(f"RP: {rp:,} / 1500 to Next Level")
    
    st.divider()
    st.metric("Treasury Credits", f"💎 {st.session_state.game_data['credits']}")

st.title("🏛️ Hungerford Holdings Command")
tabs = st.tabs(["🏛️ Board", "🚨 Critical", "📈 Finance", "⚡ Ops", "🧹 Maintenance", "💼 Isio Pursuits", "🧪 Taylor Lab", "🥂 M&A", "👴 Stakeholders"])

with tabs[0]: # Boardroom
    cols = st.columns(5)
    for i, (name, info) in enumerate(ADVISORS.items()):
        with cols[i]:
            st.image(info['img'], use_container_width=True)
            st.caption(f"**{name}**")
            st.info(info['directive'])

with tabs[2]: # Finance
    st.header("📈 The Sovereign Treasury")
    render_command_list(DATA_FINANCE, "fin")
    st.divider()
    chase = st.number_input("Chase Balance (£)", value=st.session_state.game_data['chase_bal'])
    sant = st.number_input("Santander Balance (£)", value=st.session_state.game_data['santander_bal'])
    if st.button("Sync Ledger"):
        st.session_state.game_data['chase_bal'], st.session_state.game_data['santander_bal'] = chase, sant
        update_permanent({}, "ledger_sync")

with tabs[5]: render_command_list(DATA_ISIO_PURSUITS, "isio_p", show_rp=True)
with tabs[6]: render_command_list(DATA_ISIO_TAYLOR, "isio_t", show_rp=True)

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
    with col_s: render_command_list([{"id": "hotel_p", "name": "Book Wedding Hotel", "xp": 50, "adv": "Diary Secretary", "msg": "Secure the room."}], "stake")

with tabs[3]: render_command_list(DATA_DAILY, "daily")
with tabs[4]: render_command_list(DATA_MAINTENANCE, "maint")
with tabs[7]: render_command_list(DATA_MA, "ma")
