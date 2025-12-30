import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
from pathlib import Path

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. THE PORTRAIT ENGINE (ROOT RESOLUTION) ---
# This finds the absolute path to your GitHub repo root
ROOT_DIR = Path(__file__).parent

def get_portrait(filename):
    """Explicitly resolves the path to the assets folder in GitHub."""
    target_path = ROOT_DIR / "assets" / filename
    if target_path.exists():
        return str(target_path)
    return None

# --- 3. THE SOVEREIGN REGISTRY ENGINE ---
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
        # Stats Map: B=XP, C=RP, D=Streak, E=Level, F=Credits, G=Affinity, H=Golf_Best, I=Chase, J=Santander, K=Jacq, L=MattW
        stats = {
            "xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]), 
            "level": int(row[4]), "credits": int(row[5]), "affinity": int(row[6]), 
            "golf_best": int(row[7]), "chase_bal": float(row[8]) if len(row) > 8 else 0.0,
            "santander_bal": float(row[9]) if len(row) > 9 else 0.0,
            "jacq_influence": int(row[10]) if len(row) > 10 else 50,
            "mattw_influence": int(row[11]) if len(row) > 11 else 50
        }
    except:
        stats = {"xp": 505, "rp": 0, "streak": 0, "level": 2, "credits": 50, "affinity": 50, 
                 "golf_best": 95, "chase_bal": 0.0, "santander_bal": 0.0, 
                 "jacq_influence": 50, "mattw_influence": 50}
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
    sheet1.update('B2:L2', [[g['xp'], g['rp'], g['streak'], g['level'], g['credits'], g['affinity'], 
                             g['golf_best'], g['chase_bal'], g['santander_bal'], 
                             g['jacq_influence'], g['mattw_influence']]])
    st.rerun()

# --- 4. ADVISOR DIRECTIVES ---
ADVISORS = {
    "Chief of Staff": {"img": get_portrait("cos.png"), "directive": "Louise's leave creates a leadership vacuum in London HQ. The CMgr pitch is your claim to the seat."},
    "Diary Secretary": {"img": get_portrait("diary.png"), "directive": "The 'Harrow HQ Reset' (Mould & Bedroom Audit) is essential for Friday readiness."},
    "Head of M&A": {"img": get_portrait("m_and_a.png"), "directive": "Hertsmere networking with Shivam is a dual mission: build equity and refresh Hinge photos."},
    "Portfolio Manager": {"img": get_portrait("portfolio.png"), "directive": "The CCJ strike on Jan 2nd is the primary objective of the Finance sector."},
    "Performance Coach": {"img": get_portrait("coach.png"), "directive": "40 XP Base for golf + bonus for sub-100. Target: sub-90 performance."}
}

# --- 5. TASK LEDGER ---
DATA_DAILY = [
    {"id": "skin_d", "name": "Skincare Routine", "xp": 10, "adv": "Chief of Staff", "msg": "Maintain the MD brand."},
    {"id": "supp_d", "name": "Supplement Stack", "xp": 10, "adv": "Performance Coach", "msg": "Focus on recovery tonight."},
    {"id": "stretch_d", "name": "Pre-Golf T-Spine Mobility", "xp": 15, "adv": "Performance Coach", "msg": "Crucial for Shivam's game tomorrow."}
]

DATA_MAINTENANCE = [
    {"id": "mould_p", "name": "Remove Shower Mould", "xp": 50, "adv": "Diary Secretary", "msg": "Addressing deferred maintenance."},
    {"id": "clothes_p", "name": "Bedroom Audit: Dispose Old Clothes", "xp": 80, "adv": "Diary Secretary", "msg": "Phase 1 of Reorganisation."},
    {"id": "bedroom_p", "name": "Bedroom Reorganisation", "xp": 60, "adv": "Diary Secretary", "msg": "Final recovery suite optimization."}
]

DATA_FINANCE = [
    {"id": "ccj_p", "name": "CCJ Readiness Check", "xp": 50, "urgent": True, "adv": "Portfolio Manager", "msg": "Jan 2 Strike Readiness."},
    {"id": "sant_p", "name": "Santander DD Audit", "xp": 60, "urgent": True, "adv": "Portfolio Manager", "msg": "Identify legacy DDs for Chase."}
]

DATA_ISIO_PURSUITS = [
    {"id": "snib_p", "name": "SNIB (9 Jan): Exec Summary", "rp": 120, "adv": "Chief of Staff", "msg": "HQ-grade precision for Matt W."},
    {"id": "jacq_p", "name": "Jacqueline (CMO) HQ Networking", "rp": 100, "xp": 20, "adv": "Chief of Staff", "msg": "Presence Advantage (+5 Jacq Influence)."},
    {"id": "cmgr_p", "name": "Pitch CMgr Qualification to Louise", "rp": 250, "xp": 100, "adv": "Chief of Staff", "msg": "Leadership vs Technicals."}
]

# --- 6. RENDERER ---
def render_command_list(task_list, grp, show_rp=False):
    today = str(date.today())
    completed_ids = [r['TaskID'] for r in st.session_state.history]
    for t in task_list:
        t_id, adv_name = t['id'], t['adv']
        is_done = t_id in completed_ids if t_id.endswith("_p") else any(r['TaskID'] == t_id and r['Date'] == today for r in st.session_state.history)
        if t_id.endswith("_p") and t_id in completed_ids: continue
        
        c1, c2 = st.columns([0.85, 0.15])
        with c1:
            val_str = f"+{t.get('rp', 0)} RP" if show_rp else f"+{t.get('xp', 0)} XP"
            lbl = f"✅ {t['name']}" if is_done else f"{t['name']} ({val_str})"
            if st.button(lbl, key=f"btn_{t_id}_{grp}", use_container_width=True, disabled=is_done):
                update_permanent({'xp': t.get('xp', 0), 'rp': t.get('rp', 0)}, t_id)
        with c2:
            if st.button("💬", key=f"c_{t_id}_{grp}", use_container_width=True):
                st.session_state.briefing_target = t_id
                st.rerun()
        if st.session_state.briefing_target == t_id:
            with st.container(border=True):
                col_i, col_t = st.columns([0.2, 0.8])
                with col_i:
                    img_path = ADVISORS[adv_name]['img']
                    if img_path: st.image(img_path, width=100)
                    else: st.write(f"[{adv_name}]")
                with col_t:
                    st.caption(f"**Briefing from {adv_name}**")
                    st.info(t['msg'])

# --- 7. UI LAYOUT ---
with st.sidebar:
    st.title("🎖️ Command Dashboard")
    xp, rp = st.session_state.game_data['xp'], st.session_state.game_data['rp']
    st.subheader("Life Rank Progress")
    st.progress(min((xp % 1000) / 1000, 1.0))
    st.caption(f"XP: {xp:,} / 1000 to Milestone")
    st.subheader("Career Standing")
    st.progress(min((rp % 1500) / 1500, 1.0))
    st.caption(f"RP: {rp:,} / 1500 to Next Standing")
    st.divider()
    st.metric("Treasury Credits", f"💎 {st.session_state.game_data['credits']}")

st.title("🏛️ Hungerford Holdings Command")
tabs = st.tabs(["🏛️ Board", "🚨 Critical", "📈 Finance", "⚡ Ops", "🧹 Maintenance", "💼 Isio Pursuits", "🧪 Taylor Lab", "🥂 M&A", "👴 Stakeholders"])

with tabs[0]: # Boardroom & Leadership Cabinet
    col_adv, col_cab = st.columns([0.6, 0.4])
    with col_adv:
        st.subheader("👥 Executive Committee")
        for name, info in ADVISORS.items():
            c1, c2 = st.columns([0.25, 0.75])
            with c1:
                if info['img']: st.image(info['img'], width=80)
                else: st.write(f"[{name}]")
            with c2: st.write(f"**{name}**"); st.info(info['directive'])
    with col_cab:
        st.subheader("📈 Leadership Cabinet")
        st.write(f"**Jacqueline (CMO):** {st.session_state.game_data['jacq_influence']}%")
        st.progress(st.session_state.game_data['jacq_influence'] / 100)
        st.write(f"**Matt W (Sales Director):** {st.session_state.game_data['mattw_influence']}%")
        st.progress(st.session_state.game_data['mattw_influence'] / 100)

with tabs[2]: # Finance
    st.header("📈 The Sovereign Treasury")
    render_command_list(DATA_FINANCE, "fin")
    st.divider()
    chase = st.number_input("Chase Balance (£)", value=st.session_state.game_data['chase_bal'])
    sant = st.number_input("Santander Balance (£)", value=st.session_state.game_data['santander_bal'])
    if st.button("Sync Ledger"):
        st.session_state.game_data['chase_bal'], st.session_state.game_data['santander_bal'] = chase, sant
        update_permanent({}, "ledger_sync")

with tabs[5]: render_command_list(DATA_ISIO_EB, "isio_p", show_rp=True)
with tabs[6]: # Taylor Lab
    render_command_list([{"id": "taylor_gov_p", "name": "Taylor: Governance Map", "rp": 200, "adv": "Portfolio Manager", "msg": "Enterprise Standard Audit."},
                         {"id": "taylor_sync_p", "name": "Taylor: Douglas Sync", "rp": 80, "adv": "Chief of Staff", "msg": "HQ Alignment."}], "isio_t", show_rp=True)

with tabs[8]: # Stakeholders & Golf
    st.header("👴 Stakeholder Management")
    col_g, col_s = st.columns([0.6, 0.4])
    with col_g:
        st.subheader("⛳ Hertsmere Performance Center")
        score = st.number_input("Enter Score:", 70, 120, 95)
        total_xp = 40 + max(0, 100 - score)
        if st.button(f"Log Round: {score} (+{total_xp} XP)"):
            update_permanent({'xp': total_xp}, "golf_d")
    with col_s:
        render_command_list([{"id": "hotel_p", "name": "Book Wedding Hotel", "xp": 50, "adv": "Diary Secretary", "msg": "Secure the room."}], "stake")

with tabs[3]: render_command_list(DATA_DAILY, "daily")
with tabs[4]: render_command_list(DATA_MAINTENANCE, "maint")
with tabs[7]: render_command_list([{"id": "hinge_p", "name": "Hinge Photo Audit", "xp": 100, "adv": "Head of M&A", "msg": "Cull the weak assets."}], "ma")
