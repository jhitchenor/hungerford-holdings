import streamlit as st
from datetime import datetime, date

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. SESSION STATE & ERROR MIGRATION ---
# This block prevents the KeyError by ensuring all keys exist
if 'game_data' not in st.session_state:
    st.session_state.game_data = {
        "xp": 505, 
        "rp": 0, 
        "streak": 0, 
        "level": 2, 
        "credits": 50, 
        "affinity": 50
    }

# Migration: Add missing keys to existing sessions
for key, default in {"credits": 0, "affinity": 50, "rp": 0}.items():
    if key not in st.session_state.game_data:
        st.session_state.game_data[key] = default

if 'completed_tasks' not in st.session_state:
    st.session_state.completed_tasks = set()

if 'last_reset' not in st.session_state:
    st.session_state.last_reset = str(date.today())

if 'briefing_target' not in st.session_state:
    st.session_state.briefing_target = None

# Daily Reset Logic
if st.session_state.last_reset != str(date.today()):
    st.session_state.completed_tasks = {t for t in st.session_state.completed_tasks if t.endswith("_p")}
    st.session_state.last_reset = str(date.today())

def update_stat(stat, amount, task_id):
    if task_id in st.session_state.completed_tasks:
        return
    st.session_state.game_data[stat] += amount
    st.session_state.completed_tasks.add(task_id)
    # 10% of XP turns into spendable Capital Credits
    if stat == 'xp':
        st.session_state.game_data['credits'] += int(amount * 0.1)
    st.rerun()

# --- 3. ADVISOR PROFILES ---
ADVISORS = {
    "Chief of Staff": {"img": "assets/cos.png", "title": "Strategic Oversight", "directive": "Jack, darling, focus on the SNIB bid. The partner is demanding, but the 'Win' equity is massive."},
    "Diary Secretary": {"img": "assets/diary.png", "title": "Operations", "directive": "Logistics: Ironing tonight, Hertsmere Golf tomorrow morning. Phone charging is mandatory."},
    "Head of M&A": {"img": "assets/m_and_a.png", "title": "Growth & Partnerships", "directive": "Get those golf shots tomorrow, handsome. We need fresh assets for the Hinge audit."},
    "Portfolio Manager": {"img": "assets/portfolio.png", "title": "Finance & Treasury", "directive": "CCJ Strike Day is Jan 2nd. Ensure the capital is ready for liquidation."},
    "Performance Coach": {"img": "assets/coach.png", "title": "Human Capital", "directive": "Great football match! Magnesium tonight and a deep stretch for the golf swing tomorrow."}
}

# --- 4. TASK LIBRARIES ---
DATA_DAILY = [
    {"id": "skin_d", "name": "Skincare Routine", "xp": 10, "adv": "Chief of Staff", "msg": "Maintain the brand."},
    {"id": "supp_d", "name": "Supplement Stack", "xp": 10, "adv": "Performance Coach", "msg": "Magnesium for muscle recovery."},
    {"id": "stretch_d", "name": "Pre-Golf T-Spine Stretch", "xp": 15, "adv": "Performance Coach", "msg": "Unlock that rotation for Shivam's game."},
]

DATA_MAINTENANCE = [
    {"id": "kitchen_d", "name": "Clean Kitchen", "xp": 25, "adv": "Diary Secretary", "msg": "Spotless engine room."},
    {"id": "iron_p", "name": "Iron 5 Work Shirts", "xp": 40, "adv": "Diary Secretary", "msg": "Look like a Partner on Friday."},
]

DATA_CAPITAL = [
    {"id": "ccj_p", "name": "CCJ Readiness Check", "xp": 50, "adv": "Portfolio Manager", "msg": "Verify Jan 2nd opening hours."},
    {"id": "inbox_p", "name": "Isio Inbox Recon", "xp": 75, "adv": "Chief of Staff", "msg": "Clear the noise before Friday morning."},
    {"id": "santander_p", "name": "Santander DD Audit", "xp": 60, "adv": "Portfolio Manager", "msg": "Identify DDs to move to Chase."},
]

DATA_MA = [
    {"id": "hinge_p", "name": "Visual Asset Audit: 10 Photos", "xp": 100, "adv": "Head of M&A", "msg": "Scour WhatsApp and tomorrow's golf shots."},
]

DATA_STAKEHOLDERS = [
    {"id": "golf_d", "name": "Hertsmere Golf (Shivam)", "xp": 100, "adv": "Performance Coach", "msg": "Stakeholder equity + Vitality XP."},
    {"id": "hotel_p", "name": "Book Wedding Hotel (Krishan)", "xp": 50, "urgent": True, "adv": "Diary Secretary", "msg": "URGENT: Secure the room today."},
]

# --- 5. THE BID PIPELINE ---
BIDS = [
    {"id": "snib", "name": "SNIB (Midday Fri 9 Jan)", "phase": "RFP Response", "progress": 60, "tasks": [{"id": "snib_p", "name": "Finalize Response Draft", "xp": 150, "adv": "Chief of Staff"}]},
    {"id": "yw", "name": "Yorkshire Water (10am Fri 23 Jan)", "phase": "RFP Response", "progress": 20, "tasks": [{"id": "yw_p", "name": "Technical Compliance Check", "xp": 80, "adv": "Portfolio Manager"}]},
    {"id": "c4", "name": "Channel 4 (Pitch 14 Jan)", "phase": "Pitch Prep", "progress": 40, "tasks": [{"id": "c4_p", "name": "Presentation Rehearsal", "xp": 120, "adv": "Performance Coach"}]},
    {"id": "hs2", "name": "HS2 (Expected Q1)", "phase": "Prospect", "progress": 5, "tasks": [{"id": "hs2_p", "name": "Service Line Intelligence", "xp": 50, "adv": "Chief of Staff"}]},
]

# --- 6. RENDERER ---
def render_command_list(task_list, key_grp):
    for i, t in enumerate(task_list):
        t_id = t['id']
        if t_id.endswith("_p") and t_id in st.session_state.completed_tasks:
            continue
        is_done = t_id in st.session_state.completed_tasks
        c_btn, c_chat = st.columns([0.85, 0.15])
        with c_btn:
            lbl = f"✅ {t['name']}" if is_done else f"{t['name']} (+{t['xp']} XP)"
            if st.button(lbl, key=f"btn_{t_id}", use_container_width=True, disabled=is_done):
                update_stat('xp', t['xp'], t_id)
        with c_chat:
            if st.button("💬", key=f"chat_{t_id}", use_container_width=True):
                st.session_state.briefing_target = t_id if st.session_state.briefing_target != t_id else None
                st.rerun()
        if st.session_state.briefing_target == t_id:
            with st.container(border=True):
                st.info(t['msg'])

# --- 7. UI LAYOUT ---
with st.sidebar:
    st.title(f"Level {st.session_state.game_data['level']}")
    st.metric("Corporate XP", f"{st.session_state.game_data['xp']:,}")
    st.metric("Credits", f"💎 {st.session_state.game_data['credits']}")
    st.divider()
    st.write("Relationship Affinity")
    st.progress(st.session_state.game_data['affinity'] / 100)

st.title("🏛️ Hungerford Holdings Command")
tabs = st.tabs(["🏛️ Board", "🚨 Critical", "⚡ Ops", "🧹 Maintenance", "💼 Isio Pursuit", "🥂 M&A", "👴 Stakeholders"])

with tabs[0]:
    cols = st.columns(5)
    for i, (name, info) in enumerate(ADVISORS.items()):
        with cols[i]:
            try: st.image(info['img'], use_container_width=True)
            except: st.write(f"[{name}]")
            st.info(info['directive'])

with tabs[1]:
    st.error("### 🚨 Urgent Objectives")
    crit = [t for t in DATA_STAKEHOLDERS + DATA_CAPITAL if t.get('urgent') or t['xp'] >= 100]
    render_command_list(crit, "crit")

with tabs[2]: render_command_list(DATA_DAILY, "daily")
with tabs[3]: render_command_list(DATA_MAINTENANCE, "maint")

with tabs[4]:
    st.header("💼 Pursuit
