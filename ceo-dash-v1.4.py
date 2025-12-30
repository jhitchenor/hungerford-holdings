import streamlit as st
from datetime import datetime, date

# --- 1. CORE CONFIG & STABILITY ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. SESSION STATE & ERROR MIGRATION ---
if 'game_data' not in st.session_state:
    st.session_state.game_data = {
        "xp": 505, "rp": 0, "streak": 0, "level": 2, 
        "credits": 50, "affinity": 50, "golf_best": 0
    }

# Migration: Ensure all keys exist to prevent KeyErrors
defaults = {"credits": 50, "affinity": 50, "rp": 0, "golf_best": 95}
for key, val in defaults.items():
    if key not in st.session_state.game_data:
        st.session_state.game_data[key] = val

if 'completed_tasks' not in st.session_state:
    st.session_state.completed_tasks = set()

if 'last_reset' not in st.session_state:
    st.session_state.last_reset = str(date.today())

if 'briefing_target' not in st.session_state:
    st.session_state.briefing_target = None

# Daily Reset Logic (Resets everything not ending in _p)
if st.session_state.last_reset != str(date.today()):
    st.session_state.completed_tasks = {t for t in st.session_state.completed_tasks if t.endswith("_p")}
    st.session_state.last_reset = str(date.today())

def update_stat(stat, amount, task_id):
    if task_id in st.session_state.completed_tasks:
        return
    st.session_state.game_data[stat] += amount
    st.session_state.completed_tasks.add(task_id)
    if stat == 'xp':
        st.session_state.game_data['credits'] += int(amount * 0.1)
    st.rerun()

# --- 3. ADVISOR PROFILES ---
ADVISORS = {
    "Chief of Staff": {"img": "assets/cos.png", "title": "Strategic Oversight", "directive": "Jack, darling, focus on the SNIB bid prep tonight. The midday Friday deadline is the current high-water mark for the firm."},
    "Diary Secretary": {"img": "assets/diary.png", "title": "Operations", "directive": "Hertsmere Golf tomorrow morning. Ensure the CR-V is packed and your phone is charging now. No delays."},
    "Head of M&A": {"img": "assets/m_and_a.png", "title": "Growth & Partnerships", "directive": "Get those candid shots on the green tomorrow, handsome. Authenticity beats a LoRA every time in the dating market."},
    "Portfolio Manager": {"img": "assets/portfolio.png", "title": "Finance & Treasury", "directive": "Santander audit is the priority before Jan 2nd. We must consolidate the capital into Chase immediately."},
    "Performance Coach": {"img": "assets/coach.png", "title": "Human Capital", "directive": "Great football today! Magnesium and stretching tonight. We need a fluid T-spine for your game with Shivam."}
}

# --- 4. THE COMPLETE TASK TRANCHE ---
DATA_DAILY = [
    {"id": "skin_d", "name": "Skincare Routine", "xp": 10, "adv": "Chief of Staff", "msg": "Executive image maintenance."},
    {"id": "supp_d", "name": "Supplement Stack", "xp": 10, "adv": "Performance Coach", "msg": "Focus on recovery: Magnesium and Zinc."},
    {"id": "stretch_d", "name": "Pre-Golf T-Spine Stretch", "xp": 15, "adv": "Performance Coach", "msg": "Unlock that rotation for a more powerful drive."},
]

DATA_MAINTENANCE = [
    {"id": "kitchen_d", "name": "Clean Kitchen", "xp": 25, "adv": "Diary Secretary", "msg": "Reset the engine room for the New Year."},
    {"id": "iron_p", "name": "Iron 5 Work Shirts", "xp": 40, "adv": "Diary Secretary", "msg": "The uniform of a Partner. Do it tonight."},
]

DATA_CAPITAL = [
    {"id": "ccj_p", "name": "CCJ Readiness Check", "xp": 50, "adv": "Portfolio Manager", "msg": "Verify opening hours for Jan 2nd strike."},
    {"id": "inbox_p", "name": "Isio Inbox Recon", "xp": 75, "adv": "Chief of Staff", "msg": "Reduce Friday morning friction by auditing now."},
    {"id": "santander_p", "name": "Santander DD Audit", "xp": 60, "adv": "Portfolio Manager", "msg": "Identify what needs to move to Chase."},
]

DATA_MA = [
    {"id": "hinge_p", "name": "Visual Asset Audit: 10 Photos", "xp": 100, "adv": "Head of M&A", "msg": "Archives + tomorrow's candid golf shots."},
    {"id": "apps_d", "name": "Active Networking (Apps)", "xp": 30, "adv": "Head of M&A", "msg": "Lead generation in the Marylebone/London sector."},
]

DATA_STAKEHOLDERS = [
    {"id": "golf_d", "name": "Hertsmere Golf (Shivam)", "xp": 100, "adv": "Performance Coach", "msg": "Vitality XP + Stakeholder Equity."},
    {"id": "hotel_p", "name": "Book Wedding Hotel (Krishan)", "xp": 50, "urgent": True, "adv": "Diary Secretary", "msg": "DEADLINE: Secure the room today."},
    {"id": "dad_p", "name": "Wellness Call (Dad)", "xp": 40, "adv": "Chief of Staff", "msg": "Coordinate on the IFA cash infusion."},
]

# --- 5. THE BID PIPELINE ---
BIDS = [
    {"id": "snib", "name": "SNIB (Midday Fri 9 Jan)", "phase": "RFP Response", "progress": 60, "tasks": [{"id": "snib_p", "name": "Draft SNIB Executive Summary", "xp": 150, "adv": "Chief of Staff"}]},
    {"id": "yw", "name": "Yorkshire Water (10am Fri 23 Jan)", "phase": "RFP Response", "progress": 20, "tasks": [{"id": "yw_p", "name": "YW: Technical Compliance Review", "xp": 80, "adv": "Portfolio Manager"}]},
    {"id": "c4", "name": "Channel 4 (Pitch 14 Jan)", "phase": "Pitch Prep", "progress": 40, "tasks": [{"id": "c4_p", "name": "C4: Slide Deck Architecture", "xp": 120, "adv": "Performance Coach"}]},
    {"id": "hs2", "name": "HS2 (Prospecting Phase)", "phase": "Prospect", "progress": 5, "tasks": [{"id": "hs2_p", "name": "HS2: Service Line Research", "xp": 50, "adv": "Chief of Staff"}]},
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
            if st.button(lbl, key=f"btn_{t_id}_{key_grp}", use_container_width=True, disabled=is_done):
                update_stat('xp', t['xp'], t_id)
        with c_chat:
            if st.button("💬", key=f"chat_{t_id}_{key_grp}", use_container_width=True):
                st.session_state.briefing_target = t_id if st.session_state.briefing_target != t_id else None
                st.rerun()
        if st.session_state.briefing_target == t_id:
            with st.container(border=True):
                st.markdown(f"**Briefing from {t['adv']}**")
                st.info(t['msg'])

# --- 7. UI LAYOUT ---
with st.sidebar:
    st.title(f"🎖️ Level {st.session_state.game_data['level']}")
    st.metric("Corporate XP", f"{st.session_state.game_data['xp']:,}")
    st.metric("Credits", f"💎 {st.session_state.game_data['credits']}")
    st.divider()
    st.write("Relationship Affinity")
    st.progress(st.session_state.game_data['affinity'] / 100)

st.title("🏛️ Hungerford Holdings Command")
tabs = st.tabs(["🏛️ Board", "🚨 Critical", "⚡ Ops", "🧹 Maintenance", "💼 Isio Pursuit", "🥂 M&A", "👴 Stakeholders"])

with tabs[0]: # Boardroom
    cols = st.columns(5)
    for i, (name, info) in enumerate(ADVISORS.items()):
        with cols[i]:
            try: st.image(info['img'], use_container_width=True)
            except: st.write(f"[{name}]")
            st.caption(f"**{name}**")
            st.info(info['directive'])

with tabs[1]: # Critical Path
    st.error("### 🚨 Urgent Strategic Priorities")
    all_tasks = DATA_DAILY + DATA_MAINTENANCE + DATA_CAPITAL + DATA_MA + DATA_STAKEHOLDERS
    crit = [t for t in all_tasks if t.get('urgent') or t.get('xp', 0) >= 100]
    render_command_list(crit, "crit")

with tabs[2]: render_command_list(DATA_DAILY, "daily")
with tabs[3]: render_command_list(DATA_MAINTENANCE, "maint")

with tabs[4]: # Pursuit Pipeline
    st.header("💼 Pursuit Pipeline")
    for b in BIDS:
        with st.expander(f"{b['name']} ({b['progress']}%)", expanded=True):
            st.progress(b['progress'] / 100)
            render_command_list(b['tasks'], b['id'])
    st.divider()
    render_command_list(DATA_CAPITAL, "isiocap")

with tabs[5]: render_command_list(DATA_MA, "ma")

with tabs[6]: # Stakeholders & Golf
    st.header("👴 Stakeholder Management")
    render_command_list(DATA_STAKEHOLDERS, "stake")
    st.divider()
    st.subheader("⛳ Hertsmere Scorecard")
    score = st.number_input("Enter Score for Round with Shivam:", min_value=70, max_value=120, value=95)
    if st.button("Log Score"):
        st.session_state.game_data['golf_best'] = min(score, st.session_state.game_data['golf_best'])
        st.success(f"Score of {score} logged. Performance Coach notified.")
