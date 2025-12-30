import streamlit as st
from datetime import datetime, date

# --- 1. SESSION STATE & PERSISTENCE ---
if 'game_data' not in st.session_state:
    st.session_state.game_data = {"xp": 505, "rp": 0, "streak": 0, "level": 2, "credits": 50}
    st.session_state.completed_tasks = set()
    st.session_state.last_reset = str(date.today())

def update_stat(stat, amount, task_id):
    if task_id in st.session_state.completed_tasks:
        return
    st.session_state.game_data[stat] += amount
    st.session_state.completed_tasks.add(task_id)
    if stat == 'xp':
        st.session_state.game_data['credits'] += int(amount * 0.1)
    st.rerun()

# --- 2. THE BID PORTFOLIO (Multi-Phase Data) ---
BIDS = [
    {
        "id": "snib",
        "name": "SNIB (Midday Fri 9 Jan)",
        "phase": "RFP Response",
        "progress": 60,
        "note": "Demanding Partner oversight. High precision required.",
        "tasks": [
            {"id": "snib_rfp_p", "name": "SNIB: Finalize Response Draft", "xp": 150, "adv": "Chief of Staff"},
            {"id": "snib_pitch_p", "name": "SNIB: Pitch Deck Architecture (Due 15 Jan)", "xp": 100, "adv": "Performance Coach"}
        ]
    },
    {
        "id": "c4",
        "name": "Channel 4 (Pitch 14 Jan)",
        "phase": "Pitch Prep",
        "progress": 40,
        "note": "Focus on creative delivery and stakeholder resonance.",
        "tasks": [
            {"id": "c4_rehearsal_p", "name": "C4: Pitch Rehearsal (Dry Run)", "xp": 120, "adv": "Performance Coach"}
        ]
    },
    {
        "id": "yorkshire",
        "name": "Yorkshire Water (10am Fri 23 Jan)",
        "phase": "RFP Response",
        "progress": 20,
        "note": "Steady state grind. Ensure technical compliance.",
        "tasks": [
            {"id": "yw_compliance_p", "name": "YW: Technical Compliance Check", "xp": 80, "adv": "Portfolio Manager"}
        ]
    },
    {
        "id": "hs2",
        "name": "HS2 (Prospecting Phase)",
        "phase": "Prospect",
        "progress": 5,
        "note": "Strategic intelligence gathering. New Year launch.",
        "tasks": [
            {"id": "hs2_intel_p", "name": "HS2: Multi-Service Line Research", "xp": 50, "adv": "Chief of Staff"}
        ]
    }
]

# --- 3. UI LAYOUT ---
with st.sidebar:
    st.title(f"🎖️ Level {st.session_state.game_data['level']}")
    st.metric("Corporate XP", f"{st.session_state.game_data['xp']:,}")
    st.metric("Credits", f"💎 {st.session_state.game_data['credits']}")
    st.divider()
    st.caption("Active Pipeline: 4 Bids")

st.title("🏛️ Hungerford Holdings Command")

tabs = st.tabs(["🏛️ Board", "🚨 Critical", "⚡ Ops", "🧹 Maintenance", "💼 Isio Pursuit", "🥂 M&A", "👴 Stakeholders"])

with tabs[0]: # Boardroom Directives
    st.markdown("### 👥 Executive Committee Briefing")
    cols = st.columns(5)
    directives = [
        ("Chief of Staff", "SNIB is the priority. The demanding partner requires perfection."),
        ("Diary Secretary", "Jan 9 is the wall. Everything must be ironed and prepped by then."),
        ("Head of M&A", "Dating profile audit remains scheduled for Jan 1 evening."),
        ("Portfolio Manager", "CCJ Strike date: Jan 2. Be ready."),
        ("Performance Coach", "Pre-work nutrition reset starts tomorrow.")
    ]
    for i, (name, text) in enumerate(directives):
        with cols[i]:
            st.caption(f"**{name}**")
            st.info(text)

with tabs[4]: # The New Pursuit Command
    st.header("💼 Isio Pursuit Portfolio")
    
    for bid in BIDS:
        with st.expander(f"{bid['name']} - Phase: {bid['phase']}", expanded=True):
            col_info, col_tasks = st.columns([0.4, 0.6])
            
            with col_info:
                st.write(f"**Current Status:** {bid['progress']}%")
                st.progress(bid['progress'] / 100)
                st.caption(bid['note'])
            
            with col_tasks:
                for t in bid['tasks']:
                    if t['id'] not in st.session_state.completed_tasks:
                        if st.button(f"{t['name']} (+{t['xp']} XP)", key=t['id'], use_container_width=True):
                            update_stat('xp', t['xp'], t['id'])
                    else:
                        st.write(f"✅ {t['name']}")

# ... [Maintenance, Ops, and Stakeholder rendering as per v5.5] ...
