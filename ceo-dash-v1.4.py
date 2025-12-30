import streamlit as st
from datetime import datetime, date

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. SESSION STATE & MIGRATION ---
if 'game_data' not in st.session_state:
    st.session_state.game_data = {
        "xp": 505, "rp": 0, "streak": 0, "level": 2, 
        "credits": 50, "affinity": 50, "rp_level": 1
    }

if 'completed_tasks' not in st.session_state:
    st.session_state.completed_tasks = set()

def update_stat(stat, amount, task_id):
    if task_id in st.session_state.completed_tasks:
        return
    st.session_state.game_data[stat] += amount
    st.session_state.completed_tasks.add(task_id)
    if stat == 'xp': st.session_state.game_data['credits'] += int(amount * 0.1)
    if stat == 'rp': st.session_state.game_data['credits'] += int(amount * 0.2)
    st.rerun()

# --- 3. THE ISIO "CABINET" (STAKEHOLDER DATA) ---
# Integrated into tasks below
# --- 4. TASK LIBRARIES ---

DATA_ISIO_EB = [
    {"id": "snib_p", "name": "SNIB: Midday Deadline Prep", "rp": 100, "xp": 10, "adv": "Chief of Staff", "msg": "Collaboration with Matt W (Sales Dir). He expects London-grade precision."},
    {"id": "yw_p", "name": "Yorkshire Water: Technical Compliance", "rp": 80, "xp": 5, "adv": "Portfolio Manager"},
    {"id": "indesign_p", "name": "InDesign License Acquisition", "rp": 50, "xp": 20, "adv": "Diary Secretary", "msg": "Coordination with Design Team. Elevating the visual standard of EB bids."},
]

DATA_TAYLOR_LAB = [
    {"id": "taylor_vito_p", "name": "Taylor: Governance Strategy Brief", "rp": 150, "xp": 30, "adv": "Portfolio Manager", "msg": "Objective: Appease Matt G (CTO) and Vito (CDO). Move Taylor from 'Organic' to 'Standard'."},
    {"id": "taylor_doug_p", "name": "Taylor: Logic Sync with Douglas", "rp": 80, "xp": 10, "adv": "Chief of Staff", "msg": "Syncing with your Grade C peer in Edinburgh."},
]

DATA_STRATEGIC_GROWTH = [
    {"id": "cmgr_pitch_p", "name": "The CMgr Pitch (Louise)", "rp": 200, "xp": 100, "adv": "Chief of Staff", "msg": "Convince Louise that CMgr is better for Isio's EB growth than APMP. High stakes."},
    {"id": "hq_recon_p", "name": "London HQ Networking (Jacqueline)", "rp": 120, "xp": 40, "adv": "Head of M&A", "msg": "Leverage your physical presence in HQ to build equity with the CMO."},
]

# --- 5. UI SIDEBAR (XP-BASED TITLES) ---
with st.sidebar:
    st.title(f"Level {st.session_state.game_data['level']}")
    
    # TITLES BASED ON XP (Life Progress)
    xp_total = st.session_state.game_data['xp']
    xp_titles = [
        (0, "Junior Associate"),
        (1000, "Senior Analyst"),
        (2500, "Associate Director"),
        (5000, "Managing Director"),
        (10000, "Senior Partner"),
        (20000, "Chairman of the Board")
    ]
    current_title = "Junior Associate"
    for threshold, title in xp_titles:
        if xp_total >= threshold:
            current_title = title
    
    st.subheader(f"Current Rank: {current_title}")
    st.metric("Life XP", f"{xp_total:,}")
    st.metric("Career RP", f"{st.session_state.game_data['rp']:,}")
    st.metric("Credits", f"💎 {st.session_state.game_data['credits']}")
    
    st.divider()
    st.caption("Team: Louise (Mat-leave Feb) | Douglas | Kirsty | Ed")

# --- 6. MAIN UI ---
st.title("🏛️ Hungerford Holdings Command")
tabs = st.tabs(["🏛️ Board", "🚨 Critical", "⚡ Ops", "🧹 Maintenance", "💼 Isio: EB & Pursuits", "🧪 Isio: Taylor Lab", "🥂 Growth & M&A", "👴 Stakeholders"])

with tabs[0]: # Boardroom
    st.markdown("### 👥 Executive Committee Briefing")
    cols = st.columns(5)
    directives = [
        ("Chief of Staff", "Louise leaves in Feb. The 'CMgr' pitch is your play for her seat's influence."),
        ("Diary Secretary", "InDesign license is the priority. We need the tools of the trade."),
        ("Head of M&A", "Matt W is your ally; Jacqueline is your target. Networking in HQ is vital."),
        ("Portfolio Manager", "Matt G (CTO) is unhappy. Formalize Taylor's logic or face a technical veto."),
        ("Performance Coach", "Hertsmere tomorrow. Use the golf to clear your head for the CMgr pitch.")
    ]
    for i, (name, text) in enumerate(directives):
        with cols[i]:
            st.caption(f"**{name}**")
            st.info(text)

with tabs[4]: # Isio: EB
    st.header("💼 Employee Benefits (EB) Pursuit Pipeline")
    
    st.write("**Collaborators:** Matt W (Sales Director), Ed (Grade B)")
    for t in DATA_ISIO_EB:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            if st.button(f"{t['name']} (+{t['rp']} RP / +{t['xp']} XP)", key=t['id']):
                update_stat('rp', t['rp'], t['id'])
                update_stat('xp', t['xp'], t['id'])
        with col2:
            if st.button("💬", key=f"c_{t['id']}"): st.info(t['msg'])

with tabs[5]: # Taylor Lab
    st.header("🧪 Taylor AI: Strategic R&D")
    st.write("**Stakeholders:** Matt G (CTO), Vito (CDO), Douglas (Collaborator)")
    for t in DATA_TAYLOR_LAB:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            if st.button(f"{t['name']} (+{t['rp']} RP / +{t['xp']} XP)", key=t['id']):
                update_stat('rp', t['rp'], t['id'])
                update_stat('xp', t['xp'], t['id'])
        with col2:
            if st.button("💬", key=f"c_{t['id']}"): st.info(t['msg'])

with tabs[6]: # Growth
    st.header("🥂 Strategic Career Growth")
    for t in DATA_STRATEGIC_GROWTH:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            if st.button(f"{t['name']} (+{t['rp']} RP / +{t['xp']} XP)", key=t['id']):
                update_stat('rp', t['rp'], t['id'])
                update_stat('xp', t['xp'], t['id'])
        with col2:
            if st.button("💬", key=f"c_{t['id']}"): st.info(t['msg'])

# Standard maintenance and stakeholders tabs follow...
