import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. THE PERMANENCE ENGINE (GOOGLE SHEETS) ---
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
    # Load Stats
    try:
        row = sheet1.row_values(2)
        stats = {"xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]), "level": int(row[4]), "credits": int(row[5]), "affinity": int(row[6]), "golf_best": int(row[7])}
    except:
        stats = {"xp": 505, "rp": 0, "streak": 0, "level": 2, "credits": 50, "affinity": 50, "golf_best": 95}
    
    # Load Completed Tasks
    try:
        completed = task_sheet.get_all_records()
    except:
        completed = []
    
    return stats, completed

# Initialize Session
if 'game_data' not in st.session_state:
    stats, completed = load_data()
    st.session_state.game_data = stats
    st.session_state.history = completed

def update_stat_permanent(stat, amount, task_id):
    sheet1, task_sheet = get_sheets()
    
    # 1. Update Session State
    st.session_state.game_data[stat] += amount
    if stat == 'xp': st.session_state.game_data['credits'] += int(amount * 0.1)
    if stat == 'rp': st.session_state.game_data['credits'] += int(amount * 0.2)
    
    # 2. Write to Registry
    today_str = str(date.today())
    task_sheet.append_row([today_str, task_id])
    
    # 3. Update Master Stats Row
    g = st.session_state.game_data
    sheet1.update('B2:H2', [[g['xp'], g['rp'], g['streak'], g['level'], g['credits'], g['affinity'], g['golf_best']]])
    
    st.rerun()

# --- 3. ADVISOR PROFILES ---
ADVISORS = {
    "Chief of Staff": {"img": "assets/cos.png", "directive": "Jack, Louise is watching the EB pipeline closely before her leave. CMgr is the play for leadership."},
    "Diary Secretary": {"img": "assets/diary.png", "directive": "Hertsmere tomorrow morning. I need that Wedding Hotel neutralized tonight for 'Operations Peace of Mind'."},
    "Head of M&A": {"img": "assets/m_and_a.png", "directive": "Being in the London HQ is your unfair advantage over Douglas. Leverage that proximity, handsome."},
    "Portfolio Manager": {"img": "assets/portfolio.png", "directive": "Vito and Matt G need a formal Taylor Governance map. Let's trade 'Improvised' for 'Enterprise'."},
    "Performance Coach": {"img": "assets/coach.png", "directive": "Golf XP Formula active: $40 + \max(0, 100 - strokes)$. Fight for every stroke!"}
}

# --- 4. TASK LIBRARIES ---
DATA_DAILY = [
    {"id": "skin_d", "name": "Skincare Routine", "xp": 10, "adv": "Chief of Staff"},
    {"id": "supp_d", "name": "Supplement Stack", "xp": 10, "adv": "Performance Coach"},
    {"id": "stretch_d", "name": "Pre-Golf Mobility", "xp": 15, "adv": "Performance Coach"},
]

DATA_MAINTENANCE = [
    {"id": "kitchen_d", "name": "Clean Kitchen", "xp": 25, "adv": "Diary Secretary"},
    {"id": "iron_p", "name": "Iron 5 Work Shirts", "xp": 40, "adv": "Diary Secretary"},
]

DATA_ISIO_EB = [
    {"id": "snib_p", "name": "SNIB: Response Architecture", "rp": 120, "xp": 20, "adv": "Chief of Staff"},
    {"id": "indesign_p", "name": "InDesign License Request", "rp": 50, "xp": 10, "adv": "Diary Secretary"},
    {"id": "cmgr_pitch_p", "name": "Pitch CMgr to Louise", "rp": 250, "xp": 100, "adv": "Chief of Staff"},
]

DATA_STAKEHOLDERS = [
    {"id": "hotel_p", "name": "Book Wedding Hotel (Krishan)", "xp": 50, "urgent": True, "adv": "Diary Secretary"},
    {"id": "golf_d", "name": "Hertsmere Golf (Shivam)", "xp": 40, "adv": "Performance Coach"},
]

# --- 5. RENDERER ---
def render_command_list(task_list, grp):
    today = str(date.today())
    completed_ids = [r['TaskID'] for r in st.session_state.history]
    
    for t in task_list:
        t_id = t['id']
        
        # Logic: Hide projects if in sheet; show daily tick if in sheet TODAY
        is_in_sheet = t_id in completed_ids
        was_done_today = any(r['TaskID'] == t_id and r['Date'] == today for r in st.session_state.history)
        
        if t_id.endswith("_p") and is_in_sheet:
            continue
            
        done = was_done_today if t_id.endswith("_d") else is_in_sheet
        
        c1, c2 = st.columns([0.85, 0.15])
        with c1:
            lbl = f"✅ {t['name']}" if done else f"{t['name']} (+{t.get('xp',0)} XP / +{t.get('rp',0)} RP)"
            if st.button(lbl, key=f"btn_{t_id}", use_container_width=True, disabled=done):
                if 'xp' in t: update_stat_permanent('xp', t['xp'], t_id)
                if 'rp' in t: update_stat_permanent('rp', t['rp'], t_id)
        with c2:
            if st.button("💬", key=f"c_{t_id}"): st.info(t.get('msg', "Objective under advisor review."))

# --- 6. UI ---
# (Sidebar and Tabs logic same as v6.2, but using render_command_list)
st.title("🏛️ Hungerford Holdings Command")
tabs = st.tabs(["🏛️ Board", "🚨 Critical", "⚡ Ops", "🧹 Maintenance", "💼 Isio: EB & Taylor", "🥂 Growth", "👴 Stakeholders"])

with tabs[1]:
    st.error("### 🚨 Master Priorities")
    render_command_list(DATA_STAKEHOLDERS + DATA_ISIO_EB, "crit")

with tabs[4]:
    st.header("💼 Isio Pursuit & Taylor Lab")
    render_command_list(DATA_ISIO_EB, "isio")

with tabs[6]:
    st.header("👴 Stakeholder Management")
    render_command_list(DATA_STAKEHOLDERS, "stake")
    # Scorecard logic...
