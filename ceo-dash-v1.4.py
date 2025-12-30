import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. ASSET ENGINE (Direct GitHub Raw) ---
GITHUB_BASE = "https://raw.githubusercontent.com/jhitchenor/hungerford-holdings/main/assets/"
def get_portrait_url(filename):
    return f"{GITHUB_BASE}{filename}"

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
        
        s1 = spreadsheet.worksheet("Sheet1")
        xh = spreadsheet.worksheet("XP_History")
        return s1, xh
    except Exception as e:
        # This is the 'NoneType' fix: if connection fails, we catch it here
        st.sidebar.error(f"⚠️ Registry Offline: {e}")
        return None, None

def load_data():
    sheet1, history_sheet = get_sheets()
    if not sheet1 or not history_sheet:
        # Fallback stats so the UI doesn't break
        return {"xp": 530, "rp": 0, "streak": 1, "level": 1, "credits": 50, "golf_best": 95}, []
    try:
        row = sheet1.row_values(2)
        # B=XP, C=RP, D=Streak, E=Level, F=Credits, G=Golf_PB
        stats = {
            "xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]), 
            "level": int(row[4]), "credits": int(row[5]) if len(row) > 5 else 50,
            "golf_best": int(row[6]) if len(row) > 6 else 95
        }
        history = history_sheet.get_all_records()
    except:
        stats = {"xp": 530, "rp": 0, "streak": 1, "level": 1, "credits": 50, "golf_best": 95}
        history = []
    return stats, history

# Initialize session
if 'game_data' not in st.session_state:
    stats, history = load_data()
    st.session_state.game_data = stats
    st.session_state.history = history
    st.session_state.briefing_target = None

def update_permanent(stat_updates, task_id):
    sheet1, history_sheet = get_sheets()
    
    # CRITICAL FIX: The 'NoneType' check to prevent app crashes
    if history_sheet is None or sheet1 is None:
        st.error("Action Failed: Google Sheets connection is currently unavailable.")
        return

    for stat, amount in stat_updates.items():
        st.session_state.game_data[stat] += amount
        if stat == 'xp': st.session_state.game_data['credits'] += int(amount * 0.1)
        if stat == 'rp': st.session_state.game_data['credits'] += int(amount * 0.2)
    
    g = st.session_state.game_data
    # Log to XP_History (3 columns: Date, TaskID, Total_XP)
    history_sheet.append_row([str(date.today()), task_id, g['xp']])
    
    # Update Sheet1 (B2:G2)
    sheet1.update('B2:G2', [[g['xp'], g['rp'], g['streak'], g['level'], g['credits'], g['golf_best']]])
    st.rerun()

# --- 4. ADVISOR PROFILES ---
ADVISORS = {
    "Chief of Staff": {"img": get_portrait_url("cos.png"), "directive": "Jack, the SNIB bid and Taylor logic are our high-value career assets."},
    "Diary Secretary": {"img": get_portrait_url("diary.png"), "directive": "The 'HQ Reset' (Mirror/Mould/Shirts) must be finalized tonight for Friday's deployment."},
    "Head of M&A": {"img": get_portrait_url("m_and_a.png"), "directive": "Hertsmere networking with Shivam is a dual mission: build equity and refresh Hinge photos."},
    "Portfolio Manager": {"img": get_portrait_url("portfolio.png"), "directive": "The CCJ strike on Jan 2nd is the primary objective of the Finance sector."},
    "Performance Coach": {"img": get_portrait_url("coach.png"), "directive": "40 XP Base for golf + bonus for sub-100. Every stroke matters!"}
}

# --- 5. TASK REPOSITORY (AUDITED FROM CSV) ---
DATA_DAILY = [
    {"id": "skin_d", "name": "Skincare Routine", "xp": 10, "adv": "Chief of Staff"},
    {"id": "supp_d", "name": "Supplement Stack", "xp": 10, "adv": "Performance Coach"},
    {"id": "read_d", "name": "Read for 30 mins", "xp": 20, "adv": "Chief of Staff"},
    {"id": "cook_d", "name": "Cook Meal from Scratch", "xp": 20, "adv": "Performance Coach"}
]

DATA_MAINTENANCE = [
    {"id": "iron_p", "name": "Iron 5 Work Shirts", "xp": 40, "adv": "Diary Secretary"},
    {"id": "clothes_p", "name": "Throw out old clothes", "xp": 35, "adv": "Diary Secretary"},
    {"id": "jwst_p", "name": "Hang JWST Mirror", "xp": 30, "adv": "Diary Secretary"},
    {"id": "sound_p", "name": "Hang Sound Panelling", "xp": 25, "adv": "Diary Secretary"},
    {"id": "mould_p", "name": "Remove Shower Mould", "xp": 50, "adv": "Diary Secretary"},
    {"id": "bedroom_p", "name": "Bedroom Reorganisation", "xp": 60, "adv": "Diary Secretary"}
]

DATA_ISIO_RP = [
    {"id": "snib_julie_p", "name": "SNIB (9 Jan): Julie Review Prep", "rp": 120, "adv": "Chief of Staff"},
    {"id": "jen_p", "name": "Jen: Modular Deck Update", "rp": 150, "adv": "Chief of Staff"},
    {"id": "taylor_gov_p", "name": "Taylor: Governance Strategy", "rp": 200, "adv": "Portfolio Manager"},
    {"id": "office_d", "name": "Isio HQ Day (London)", "rp": 30, "adv": "Chief of Staff"}
]

DATA_ATHLETIC = [
    {"id": "padel_p", "name": "Organise Padel", "xp": 10, "adv": "Performance Coach"},
    {"id": "mid_foot_play_d", "name": "Play Midweek Football", "xp": 25, "adv": "Performance Coach"},
    {"id": "squash_p", "name": "Play Squash", "xp": 40, "adv": "Performance Coach"}
]

DATA_STAKEHOLDERS = [
    {"id": "hotel_p", "name": "Book Wedding Hotel (Krishan)", "xp": 50, "urgent": True, "adv": "Diary Secretary"},
    {"id": "dad_p", "name": "Wellness Call (Dad)", "xp": 40, "adv": "Chief of Staff"}
]

# --- 6. RENDERER ---
def render_command_list(task_list, grp, show_rp=False):
    today = str(date.today())
    completed_ids = [str(r.get('TaskID', '')) for r in st.session_state.history]
    for t in task_list:
        t_id, adv_name = t['id'], t['adv']
        is_done = t_id in completed_ids if t_id.endswith("_p") else any(str(r.get('TaskID','')) == t_id and str(r.get('Date','')) == today for r in st.session_state.history)
        if t_id.endswith("_p") and is_done: continue
        
        c1, c2 = st.columns([0.85, 0.15])
        with c1:
            lbl = f"✅ {t['name']}" if is_done else f"{t['name']} (+{t.get('rp' if show_rp else 'xp', 0)} {'RP' if show_rp else 'XP'})"
            if st.button(lbl, key=f"btn_{t_id}_{grp}", use_container_width=True, disabled=is_done):
                update_permanent({'xp': t.get('xp', 0), 'rp': t.get('rp', 0)}, t_id)
        with c2:
            if st.button("💬", key=f"c_{t_id}_{grp}", use_container_width=True):
                st.session_state.briefing_target = t_id
                st.rerun()
        if st.session_state.briefing_target == t_id:
            with st.container(border=True):
                ci, ct = st.columns([0.2, 0.8]); ci.image(ADVISORS[adv_name]['img'], width=80)
                ct.caption(f"**Briefing from {adv_name}**"); ct.info(t.get('msg', "Advisors monitoring active."))

# --- 7. UI ---
with st.sidebar:
    st.title("🎖️ Command Dashboard")
    xp, rp = st.session_state.game_data['xp'], st.session_state.game_data['rp']
    st.subheader("Life XP")
    st.progress(min((xp % 1000) / 1000, 1.0)); st.caption(f"Total XP: {xp:,}")
    st.subheader("Career RP")
    st.progress(min((rp % 1500) / 1500, 1.0)); st.caption(f"Total RP: {rp:,}")
    st.divider(); st.metric("Credits", f"💎 {st.session_state.game_data['credits']}")

st.title("🏛️ Hungerford Holdings Command")
tabs = st.tabs(["🏛️ Board", "🚨 Critical", "📈 Finance", "⚡ Ops", "🧹 Maintenance", "💼 Isio Pursuits", "🧪 Taylor Lab", "🥂 M&A", "👴 Stakeholders"])

with tabs[0]:
    cols = st.columns(5)
    for i, (name, info) in enumerate(ADVISORS.items()):
        with cols[i]: st.image(info['img'], use_container_width=True); st.info(info['directive'])

with tabs[2]: render_command_list([{"id":"ccj_p","name":"CCJ Strike Readiness","xp":50,"adv":"Portfolio Manager"}], "fin")
with tabs[4]: render_command_list(DATA_MAINTENANCE, "maint")
with tabs[5]: render_command_list(DATA_ISIO_RP, "isio_p", show_rp=True)
with tabs[6]: render_command_list([t for t in DATA_ISIO_RP if "taylor" in t['id']], "isio_t", show_rp=True)
with tabs[8]: # Stakeholders & Golf
    st.header("👴 Stakeholder Management")
    col_g, col_s = st.columns([0.6, 0.4])
    with col_g:
        st.subheader("⛳ Hertsmere Performance Center")
        score = st.number_input("Enter Score:", 70, 120, 95)
        total_xp = 40 + max(0, 100 - score)
        if st.button(f"Log Round: {score} (+{total_xp} XP)"): update_permanent({'xp': total_xp}, "golf_d")
    with col_s: render_command_list(DATA_STAKEHOLDERS, "stake")
with tabs[3]: render_command_list(DATA_DAILY, "daily")
