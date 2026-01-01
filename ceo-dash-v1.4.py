import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. ASSET ENGINE (GitHub Raw Resolution) ---
GITHUB_BASE = "https://raw.githubusercontent.com/jhitchenor/hungerford-holdings/main/assets/"
def get_portrait(filename):
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
        return spreadsheet.worksheet("Sheet1"), spreadsheet.worksheet("XP_History")
    except Exception as e:
        st.error(f"Registry Connection Error: {e}")
        return None, None

def load_data():
    sheet1, history_sheet = get_sheets()
    if not sheet1:
        return {"xp": 600, "rp": 0, "streak": 1, "level": 1, "credits": 8, "golf_best": 95}, []
    try:
        row = sheet1.row_values(2)
        # B=XP, C=RP, D=Streak, E=Level, F=Credits, G=Golf_PB
        stats = {
            "xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]), 
            "level": int(row[4]), "credits": int(row[5]), "golf_best": int(row[6])
        }
        history = history_sheet.get_all_records()
    except:
        stats = {"xp": 600, "rp": 0, "streak": 1, "level": 1, "credits": 8, "golf_best": 95}
        history = []
    return stats, history

if 'game_data' not in st.session_state:
    stats, history = load_data()
    st.session_state.game_data, st.session_state.history = stats, history
    st.session_state.briefing_target = None

def update_permanent(stat_updates, task_id):
    sheet1, history_sheet = get_sheets()
    if not history_sheet: return
    for stat, amount in stat_updates.items():
        st.session_state.game_data[stat] += amount
        if stat == 'xp': st.session_state.game_data['credits'] += int(amount * 0.1)
        if stat == 'rp': st.session_state.game_data['credits'] += int(amount * 0.2)
    g = st.session_state.game_data
    history_sheet.append_row([str(date.today()), task_id, g['xp']])
    sheet1.update('B2:G2', [[g['xp'], g['rp'], g['streak'], g['level'], g['credits'], g['golf_best']]])
    st.rerun()

# --- 4. ADVISOR PROFILES ---
ADVISORS = {
    "Chief of Staff": {"img": get_portrait("cos.png"), "directive": "Jack, the SNIB bid and Taylor logic are our high-value career assets."},
    "Diary Secretary": {"img": get_portrait("diary.png"), "directive": "The 'HQ Reset' (Mirror/Mould/Shirts) must be finalized tonight for Friday's deployment."},
    "Head of M&A": {"img": get_portrait("m_and_a.png"), "directive": "Social and Romantic are XP assets. Keep the Hinge asset audit moving."},
    "Portfolio Manager": {"img": get_portrait_url("portfolio.png"), "directive": "The CCJ strike on Jan 2nd is the primary financial objective."},
    "Performance Coach": {"img": get_portrait("coach.png"), "directive": "Vitality logic: 40 XP Base for golf + bonus for sub-100 performance."}
}

# --- 5. TASK REPOSITORY (FULL CSV AUDIT) ---
DATA_DAILY = [{"id": "skin_d", "name": "Skincare Routine", "xp": 10, "adv": "Chief of Staff"},
              {"id": "supp_d", "name": "Supplement Stack", "xp": 10, "adv": "Performance Coach"},
              {"id": "read_d", "name": "Read for 30 mins", "xp": 20, "adv": "Chief of Staff"},
              {"id": "cook_d", "name": "Cook Meal from Scratch", "xp": 20, "adv": "Performance Coach"}]

DATA_MAINTENANCE = [{"id": "iron_p", "name": "Iron 5 Work Shirts", "xp": 40, "adv": "Diary Secretary"},
                    {"id": "clothes_p", "name": "Dispose Old Clothes", "xp": 35, "adv": "Diary Secretary"},
                    {"id": "jwst_p", "name": "Hang JWST Mirror", "xp": 30, "adv": "Diary Secretary"},
                    {"id": "sound_p", "name": "Hang Sound Panelling", "xp": 25, "adv": "Diary Secretary"},
                    {"id": "vinyls_p", "name": "Hang Vinyls", "xp": 20, "adv": "Diary Secretary"},
                    {"id": "mould_p", "name": "Remove Shower Mould", "xp": 50, "adv": "Diary Secretary"},
                    {"id": "bedroom_p", "name": "Bedroom Reorganisation", "xp": 60, "adv": "Diary Secretary"},
                    {"id": "goals_p", "name": "Write 2026 Goals", "xp": 25, "adv": "Chief of Staff"}]

DATA_ISIO = [{"id": "snib_p", "name": "SNIB (9 Jan): Julie Review Prep", "rp": 120, "adv": "Chief of Staff"},
             {"id": "c4_p", "name": "C4 (14 Jan): Draft Pitch Doc", "rp": 100, "adv": "Chief of Staff"},
             {"id": "jen_p", "name": "Jen: Modular Deck Update", "rp": 150, "adv": "Chief of Staff"},
             {"id": "jon_p", "name": "Jon: DC Governance Deck", "rp": 150, "adv": "Portfolio Manager"},
             {"id": "taylor_gov_p", "name": "Taylor: Governance Strategy", "rp": 200, "adv": "Portfolio Manager"},
             {"id": "office_d", "name": "Isio HQ Day (London)", "rp": 30, "adv": "Chief of Staff"},
             {"id": "jacq_p", "name": "Jacqueline (CMO) Networking", "rp": 100, "adv": "Chief of Staff"},
             {"id": "cmgr_p", "name": "Pitch CMgr to Louise", "rp": 250, "adv": "Chief of Staff"}]

DATA_ATHLETIC = [{"id": "padel_p", "name": "Organise Padel", "xp": 10, "adv": "Performance Coach"},
                 {"id": "sun_foot_play_d", "name": "Play Sunday Football", "xp": 25, "adv": "Performance Coach"},
                 {"id": "mid_foot_play_d", "name": "Play Midweek Football", "xp": 25, "adv": "Performance Coach"},
                 {"id": "squash_p", "name": "Play Squash", "xp": 40, "adv": "Performance Coach"},
                 {"id": "golf_lessons_p", "name": "Book Golf Lessons", "xp": 10, "adv": "Performance Coach"}]

DATA_STAKEHOLDERS = [{"id": "hotel_p", "name": "Book Wedding Hotel (Krishan)", "xp": 50, "urgent": True, "adv": "Diary Secretary"},
                     {"id": "poker_p", "name": "Organise Poker Night", "xp": 20, "adv": "Head of M&A"},
                     {"id": "dad_p", "name": "Wellness Call (Dad)", "xp": 40, "adv": "Chief of Staff"}]

DATA_MA = [{"id": "hinge_d", "name": "Open up Hinge", "xp": 10, "adv": "Head of M&A"},
           {"id": "hinge_pics_p", "name": "Find 5 Hinge Pictures", "xp": 80, "adv": "Head of M&A"},
           {"id": "date_p", "name": "Went on a Date", "xp": 100, "adv": "Head of M&A"}]

# --- 6. RENDERER ---
def render_command_list(task_list, grp, show_rp=False):
    today = str(date.today())
    completed_ids = [str(r.get('TaskID', '')) for r in st.session_state.history]
    for t in task_list:
        t_id, adv_name = t['id'], t['adv']
        is_done_ever = t_id in completed_ids
        is_done_today = any(str(r.get('TaskID','')) == t_id and str(r.get('Date','')) == today for r in st.session_state.history)
        if t_id.endswith("_p") and is_done_ever: continue
        done = is_done_today if t_id.endswith("_d") else is_done_ever
        c1, c2 = st.columns([0.85, 0.15])
        with c1:
            lbl = f"✅ {t['name']}" if done else f"{t['name']} (+{t.get('rp' if show_rp else 'xp', 0)} {'RP' if show_rp else 'XP'})"
            if st.button(lbl, key=f"btn_{t_id}_{grp}", use_container_width=True, disabled=done):
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
tabs = st.tabs(["🏛️ Board", "🚨 Critical", "📈 Finance", "⚡ Ops", "🏃 Athletic", "🧹 Maintenance", "💼 Isio Pursuits", "🧪 Taylor Lab", "🥂 M&A", "👴 Stakeholders"])

with tabs[0]:
    cols = st.columns(5)
    for i, (name, info) in enumerate(ADVISORS.items()):
        with cols[i]: st.image(info['img'], use_container_width=True); st.info(info['directive'])

with tabs[1]:
    st.error("### 🚨 Urgent Master Objectives")
    all_t = DATA_MAINTENANCE + DATA_ISIO + DATA_STAKEHOLDERS
    render_command_list([t for t in all_t if t.get('urgent') or t.get('xp', 0) >= 100], "crit")

with tabs[2]: # Finance
    st.header("📈 Financial Objectives")
    render_command_list([{"id":"ccj_p","name":"CCJ Strike Readiness","xp":50,"adv":"Portfolio Manager"}], "fin")

with tabs[4]: render_command_list(DATA_ATHLETIC, "ath")
with tabs[5]: render_command_list(DATA_MAINTENANCE, "maint")
with tabs[6]: render_command_list(DATA_ISIO, "isio_p", show_rp=True)
with tabs[7]: render_command_list([t for t in DATA_ISIO if "taylor" in t['id']], "isio_t", show_rp=True)

with tabs[9]: # Stakeholders & Golf
    st.header("👴 Stakeholder Management")
    col_g, col_s = st.columns([0.6, 0.4])
    with col_g:
        st.subheader("⛳ Hertsmere Performance Center")
        score = st.number_input("Enter Score:", 70, 120, 95)
        total_xp = 40 + max(0, 100 - score)
        if st.button(f"Log Round: {score} (+{total_xp} XP)"): update_permanent({'xp': total_xp}, "golf_d")
    with col_s: render_command_list(DATA_STAKEHOLDERS, "stake")

with tabs[3]: render_command_list(DATA_DAILY, "daily")
with tabs[8]: render_command_list(DATA_MA, "ma")
