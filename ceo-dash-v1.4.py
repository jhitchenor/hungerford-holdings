import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
import os

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. DATA PERSISTENCE ENGINE ---
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
        
        # Safety Check: Ensure worksheets exist
        sheet1 = spreadsheet.worksheet("Sheet1")
        try:
            task_sheet = spreadsheet.worksheet("Completed_Tasks")
        except gspread.exceptions.WorksheetNotFound:
            # Create it if it's missing to prevent the append_row error
            task_sheet = spreadsheet.add_worksheet(title="Completed_Tasks", rows="100", cols="20")
            task_sheet.append_row(["Date", "TaskID"])
            
        return sheet1, task_sheet
    except Exception as e:
        st.error(f"Master Registry Connection Error: {e}")
        return None, None

def load_data():
    sheet1, task_sheet = get_sheets()
    if not sheet1:
        return {"xp": 505, "rp": 0, "streak": 0, "level": 2, "credits": 50, "affinity": 50, "golf_best": 95, "chase_bal": 0.0, "santander_bal": 0.0, "jacq_influence": 50, "mattw_influence": 50}, []
    
    try:
        row = sheet1.row_values(2)
        stats = {
            "xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]), 
            "level": int(row[4]), "credits": int(row[5]), "affinity": int(row[6]), 
            "golf_best": int(row[7]), "chase_bal": float(row[8]) if len(row) > 8 else 0.0,
            "santander_bal": float(row[9]) if len(row) > 9 else 0.0,
            "jacq_influence": int(row[10]) if len(row) > 10 else 50,
            "mattw_influence": int(row[11]) if len(row) > 11 else 50
        }
        completed = task_sheet.get_all_records()
    except:
        stats = {"xp": 505, "rp": 0, "streak": 0, "level": 2, "credits": 50, "affinity": 50, "golf_best": 95, "chase_bal": 0.0, "santander_bal": 0.0, "jacq_influence": 50, "mattw_influence": 50}
        completed = []
    return stats, completed

if 'game_data' not in st.session_state:
    stats, completed = load_data()
    st.session_state.game_data = stats
    st.session_state.history = completed
    st.session_state.briefing_target = None

def update_permanent(stat_updates, task_id):
    sheet1, task_sheet = get_sheets()
    if not task_sheet:
        st.error("Critical Error: Completed_Tasks sheet not found. Data cannot be saved.")
        return

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

# --- 3. ADVISOR PROFILES ---
ADVISORS = {
    "Chief of Staff": {"img": "assets/cos.png", "directive": "Jack, Louise's leave in Feb is your window. Focus on HQ influence and the CMgr pitch."},
    "Diary Secretary": {"img": "assets/diary.png", "directive": "Operational hygiene is the priority. The 'Harrow Reset' must be completed tonight."},
    "Head of M&A": {"img": "assets/m_and_a.png", "directive": "Fresh photos at Hertsmere tomorrow. Authenticity is the primary asset for the Hinge audit."},
    "Portfolio Manager": {"img": "assets/portfolio.png", "directive": "Audit the legacy Santander account. We need full liquidity in Chase for the CCJ strike."},
    "Performance Coach": {"img": "assets/coach.png", "directive": "Base XP for golf is 40. Target is a sub-90 score for the efficiency dividend."}
}

# --- 4. COMPREHENSIVE TASK LIBRARIES (CSV AUDIT) ---

DATA_DAILY = [
    {"id": "skin_d", "name": "Skincare Routine", "xp": 10, "adv": "Chief of Staff", "msg": "Brand maintenance."},
    {"id": "supp_d", "name": "Supplement Stack", "xp": 10, "adv": "Performance Coach", "msg": "Recovery protocol."},
    {"id": "stretch_d", "name": "Pre-Golf T-Spine Mobility", "xp": 15, "adv": "Performance Coach", "msg": "Unlock rotation for the 1st tee."},
    {"id": "cook_d", "name": "Cook Meal from Scratch", "xp": 20, "adv": "Performance Coach", "msg": "Fuel integrity."},
    {"id": "office_d", "name": "Isio HQ Day (London)", "xp": 15, "rp": 20, "adv": "Chief of Staff", "msg": "Face-time with Jacqueline and Matt W."}
]

DATA_ATHLETIC = [
    {"id": "range_d", "name": "Driving Range Session", "xp": 15, "adv": "Performance Coach"},
    {"id": "padel_p", "name": "Organise Padel Game", "xp": 10, "adv": "Performance Coach"},
    {"id": "sun_foot_org_d", "name": "Organise Sunday Football (Wed)", "xp": 5, "adv": "Performance Coach"},
    {"id": "sun_foot_play_d", "name": "Play Sunday Football", "xp": 25, "adv": "Performance Coach"},
    {"id": "mid_foot_play_d", "name": "Play Midweek Football", "xp": 25, "adv": "Performance Coach"},
    {"id": "squash_p", "name": "Play Squash", "xp": 40, "adv": "Performance Coach"},
    {"id": "golf_lessons_p", "name": "Book Golf Lessons", "xp": 10, "adv": "Performance Coach"}
]

DATA_MAINTENANCE = [
    {"id": "mould_p", "name": "Remove Shower Mould", "xp": 50, "adv": "Diary Secretary"},
    {"id": "clothes_p", "name": "Dispose Old Clothes", "xp": 35, "adv": "Diary Secretary", "msg": "CSV Audit: 35 XP value confirmed."},
    {"id": "bedroom_p", "name": "Bedroom Reorganisation", "xp": 60, "adv": "Diary Secretary"},
    {"id": "jwst_p", "name": "Hang JWST Mirror over stairs", "xp": 30, "adv": "Diary Secretary"},
    {"id": "sound_p", "name": "Hang Sound Panelling", "xp": 25, "adv": "Diary Secretary"},
    {"id": "vinyls_p", "name": "Hang Vinyls", "xp": 20, "adv": "Diary Secretary"},
    {"id": "putt_mat_p", "name": "Reposition Putting/Mats", "xp": 20, "adv": "Performance Coach"},
    {"id": "goals_p", "name": "Write Goals", "xp": 25, "adv": "Chief of Staff"},
    {"id": "takeaway_p", "name": "Week Without Takeaways", "xp": 100, "adv": "Performance Coach"}
]

DATA_ISIO_RP = [
    {"id": "snib_julie_p", "name": "SNIB Proposal: Julie Review Prep", "rp": 100, "adv": "Chief of Staff"},
    {"id": "c4_pitch_p", "name": "C4: Draft Pitch Document", "rp": 120, "adv": "Performance Coach"},
    {"id": "jen_p", "name": "Jen Project: Modular Decks", "rp": 150, "adv": "Chief of Staff"},
    {"id": "jon_p", "name": "Jon Project: DC Governance Deck", "rp": 150, "adv": "Portfolio Manager"},
    {"id": "diff_p", "name": "Sub-proposition Differentiators", "rp": 80, "adv": "Chief of Staff"},
    {"id": "website_p", "name": "Website Changes (Flex Platform)", "rp": 70, "adv": "Portfolio Manager"},
    {"id": "faces_p", "name": "Update Faces Deck", "rp": 60, "adv": "Chief of Staff"},
    {"id": "pitch_prac_p", "name": "Schedule Pitch Practice", "rp": 40, "adv": "Performance Coach"},
    {"id": "pursuit_win_p", "name": "Won a Pursuit at Work", "rp": 250, "xp": 50, "adv": "Chief of Staff"}
]

DATA_STAKEHOLDERS_SOCIAL = [
    {"id": "hotel_p", "name": "Book Wedding Hotel (Krishan)", "xp": 50, "urgent": True, "adv": "Diary Secretary"},
    {"id": "poker_p", "name": "Organise Poker Night", "xp": 20, "adv": "Head of M&A"},
    {"id": "tracey_p", "name": "See Tracey", "xp": 30, "adv": "Head of M&A"},
    {"id": "amir_p", "name": "See Amir", "xp": 30, "adv": "Head of M&A"},
    {"id": "yas_p", "name": "See Yas and Cullen", "xp": 40, "adv": "Head of M&A"},
    {"id": "dad_p", "name": "Wellness Call (Dad)", "xp": 40, "adv": "Chief of Staff"}
]

DATA_MA = [
    {"id": "hinge_d", "name": "Open up Hinge", "xp": 10, "adv": "Head of M&A"},
    {"id": "hinge_pics_p", "name": "Find 5 Good Pictures", "xp": 80, "adv": "Head of M&A"},
    {"id": "date_p", "name": "Went on a Date", "xp": 100, "adv": "Head of M&A"}
]

# --- 5. RENDERER ---
def render_command_list(task_list, grp, show_rp=False):
    today = str(date.today())
    completed_ids = [r['TaskID'] for r in st.session_state.history]
    for t in task_list:
        t_id, adv_name = t['id'], t['adv']
        is_done = t_id in completed_ids if t_id.endswith("_p") else any(r['TaskID'] == t_id and r['Date'] == today for r in st.session_state.history)
        if t_id.endswith("_p") and is_done: continue
        
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
                ci, ct = st.columns([0.2, 0.8])
                with ci:
                    if os.path.exists(ADVISORS[adv_name]['img']): st.image(ADVISORS[adv_name]['img'], width=80)
                    else: st.warning(f"File missing: {ADVISORS[adv_name]['img']}")
                with ct: st.caption(f"**Briefing from {adv_name}**"); st.info(t['msg'])

# --- 6. UI ---
with st.sidebar:
    st.title("🎖️ MD Command")
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
tabs = st.tabs(["🏛️ Board", "🚨 Critical", "📈 Finance", "⚡ Ops", "🏃 Athletic", "🧹 Maintenance", "💼 Isio Pursuits", "🧪 Taylor Lab", "🥂 M&A", "👴 Stakeholders"])

with tabs[0]: # Boardroom
    cols = st.columns(5)
    for i, (name, info) in enumerate(ADVISORS.items()):
        with cols[i]:
            if os.path.exists(info['img']): st.image(info['img'], use_container_width=True)
            else: st.error(f"Missing {name} portrait")
            st.info(info['directive'])

with tabs[2]: # Finance
    st.header("📈 The Sovereign Treasury")
    render_command_list([{"id":"ccj_p","name":"CCJ Readiness Check","xp":50,"adv":"Portfolio Manager","msg":"Jan 2 Strike Readiness."}], "fin")
    st.divider()
    chase = st.number_input("Chase Balance (£)", value=st.session_state.game_data['chase_bal'])
    sant = st.number_input("Santander Balance (£)", value=st.session_state.game_data['santander_bal'])
    if st.button("Sync Ledger"):
        st.session_state.game_data['chase_bal'], st.session_state.game_data['santander_bal'] = chase, sant
        update_permanent({}, "ledger_sync")

with tabs[4]: render_command_list(DATA_ATHLETIC, "ath")
with tabs[5]: render_command_list(DATA_MAINTENANCE, "maint")
with tabs[6]: render_command_list(DATA_ISIO_RP, "isio_p", show_rp=True)

with tabs[9]: # Stakeholders & Golf
    st.header("👴 Stakeholder Management")
    col_g, col_s = st.columns([0.6, 0.4])
    with col_g:
        st.subheader("⛳ Hertsmere Performance Center")
        score = st.number_input("Enter Score:", 70, 120, 95)
        total_xp = 40 + max(0, 100 - score)
        if st.button(f"Log Round: {score} (+{total_xp} XP)"):
            update_permanent({'xp': total_xp}, "golf_d")
    with col_s: render_command_list(DATA_STAKEHOLDERS_SOCIAL, "stake")

with tabs[3]: render_command_list(DATA_DAILY, "daily")
with tabs[8]: render_command_list(DATA_MA, "ma")
