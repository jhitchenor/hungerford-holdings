import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. DATA ENGINE ---
def get_gsheet(sheet_name="Sheet1"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("your_key_file.json", scope)
        client = gspread.authorize(creds)
        SPREADSHEET_ID = "1wZSAKq283Q1xf9FAeMBIw403lpavRRAVLKNntc950Og" 
        return client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
    except: return None

def load_game_data():
    default_data = {"xp": 505, "rp": 0, "streak": 0, "level": 2}
    try:
        sheet = get_gsheet("Sheet1")
        if sheet:
            row = sheet.row_values(2)
            data = {"xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]), "level": int(row[4])}
            if data["xp"] >= 500 and data["level"] == 1: data["level"] = 2
            return data
        return default_data
    except: return default_data

if 'game_data' not in st.session_state:
    st.session_state.game_data = load_game_data()

# Track which task is currently "Briefing"
if 'briefing_target' not in st.session_state:
    st.session_state.briefing_target = None

def update_stat(stat, amount, is_urgent=False):
    multiplier = 1.5 if is_urgent else 1.0
    st.session_state.game_data[stat] += int(amount * multiplier)
    xp_needed = st.session_state.game_data['level'] * 500
    if st.session_state.game_data['xp'] >= xp_needed:
        st.session_state.game_data['level'] += 1
        st.balloons()
    st.rerun()

# --- 3. ADVISOR PROFILES ---
ADVISORS = {
    "Chief of Staff": {
        "img": "assets/cos.png", 
        "title": "Strategic Oversight",
        "directive": "Jack, darling, we need the CCJ cleared. It's the primary anchor holding back our momentum."
    },
    "Diary Secretary": {
        "img": "assets/diary.png", 
        "title": "Operations",
        "directive": "Logistics check: The Harrow HQ needs a reset tonight. Efficiency in your surroundings dictates efficiency in your bids."
    },
    "Head of M&A": {
        "img": "assets/m_and_a.png", 
        "title": "Growth & Partnerships",
        "directive": "You're a high-value asset, handsome. High-growth happens in the West End. Let's expand our search radius."
    },
    "Portfolio Manager": {
        "img": "assets/portfolio.png", 
        "title": "Finance & Treasury",
        "directive": "The numbers don't lie. Update the budget tracker today to ensure total liquidity for our 2026 projects."
    },
    "Performance Coach": {
        "img": "assets/coach.png", 
        "title": "Human Capital",
        "directive": "Let's go, Champ! That golf swing needs mobility. 15 minutes of stretching is a direct investment in power."
    }
}

# --- 4. THE COMPLETE TASK TRANCHE ---
DATA_DAILY = [
    {"name": "Skincare Routine", "xp": 10, "adv": "Chief of Staff", "msg": "Maintain the brand, Jack. Looking the part is half the battle."},
    {"name": "Supplement Stack", "xp": 10, "adv": "Performance Coach", "msg": "Fuel your brain, Champ! High-octane petrol for your mind!"},
    {"name": "15 mins stretching", "xp": 15, "adv": "Performance Coach", "msg": "Let's get that T-spine rotation back for the fairway!"},
    {"name": "Practice Putting ⛳", "xp": 15, "adv": "Performance Coach", "msg": "20 reps. Golf is won on the green."},
    {"name": "Read for 30 mins", "xp": 25, "adv": "Chief of Staff", "msg": "Deep literacy is a competitive advantage. Focus, darling."},
]

DATA_MAINT = [
    {"name": "Clean Kitchen", "xp": 25, "adv": "Diary Secretary", "msg": "The engine room of the home must be spotless."},
    {"name": "Clean Lounge", "xp": 25, "adv": "Diary Secretary", "msg": "Reset the environment for relaxation."},
    {"name": "Clean Bathroom", "xp": 30, "adv": "Diary Secretary", "msg": "High-standard hygiene maintenance."},
    {"name": "Remove Shower Mould", "xp": 40, "adv": "Diary Secretary", "msg": "Address deferred maintenance immediately."},
]

DATA_CAPITAL = [
    {"name": "Update budget tracker", "xp": 50, "adv": "Portfolio Manager", "msg": "Liquidity is king. Accuracy is the foundation of freedom."},
    {"name": "Plan next week's meals", "xp": 50, "adv": "Performance Coach", "msg": "Fuel planning prevents poor performance."},
    {"name": "Reorganise Bedroom", "xp": 80, "adv": "Diary Secretary", "msg": "Your bedroom is your recovery suite."},
    {"name": "CCJ: Evidence/Filing", "xp": 200, "urgent": True, "adv": "Portfolio Manager", "msg": "Priority one audit. Record every timestamp."},
]

DATA_ISIO = [
    {"name": "Gov/Client Research", "xp": 40, "adv": "Chief of Staff", "msg": "Information is the primary currency of a bid manager."},
    {"name": "Deep work on CCJ project", "xp": 100, "adv": "Chief of Staff", "msg": "Focus, Jack. 90 minutes of flow will slay this beast."},
    {"name": "Bid/Pursuit Sprint", "rp": 100, "adv": "Chief of Staff", "msg": "Isio's growth depends on this pursuit. Deliver excellence."}
]

DATA_MA = [
    {"name": "Active Networking (Apps)", "xp": 30, "adv": "Head of M&A", "msg": "Keep the pipeline full, handsome. Outreach never stops."},
    {"name": "Style & Grooming", "xp": 40, "adv": "Head of M&A", "msg": "Packaging is 50% of the sale."},
    {"name": "First Round Date", "xp": 100, "adv": "Head of M&A", "msg": "Initial due diligence. Assess her values."},
    {"name": "Central London Venture", "xp": 150, "adv": "Head of M&A", "msg": "Expand your territory beyond the Harrow border."}
]

DATA_STAKE = [
    {"name": "Weekly Wellness Call (Dad)", "xp": 40, "adv": "Chief of Staff", "msg": "Strategic check-in. His stability is your stability."},
    {"name": "Book Wedding Hotel", "xp": 50, "urgent": True, "adv": "Diary Secretary", "msg": "Secure the lodging today. Social rep is on the line."},
    {"name": "Visit Hungerford", "xp": 150, "adv": "Chief of Staff", "msg": "Presence is the highest-value investment."}
]

# --- 5. RENDERER (CONVENTIONAL & NESTED) ---
def render_command_list(task_list, key_group):
    for i, t in enumerate(task_list):
        # Create unique key for the container logic
        task_id = f"{key_group}_{i}"
        
        c_btn, c_chat = st.columns([0.85, 0.15])
        val = t.get('xp', t.get('rp', 0))
        unit = "XP" if 'xp' in t else "RP"
        stat = 'xp' if 'xp' in t else 'rp'

        with c_btn:
            if st.button(f"{t['name']} (+{val} {unit})", key=f"btn_{task_id}", use_container_width=True):
                update_stat(stat, val, is_urgent=t.get('urgent', False))
        
        with c_chat:
            if st.button("💬", key=f"chat_{task_id}", use_container_width=True):
                st.session_state.briefing_target = task_id if st.session_state.briefing_target != task_id else None
                st.rerun()

        # BRIEFING DISPLAY (Directly below task)
        if st.session_state.briefing_target == task_id:
            with st.container(border=True):
                col_img, col_txt = st.columns([0.2, 0.8])
                with col_img:
                    st.image(ADVISORS[t['adv']]['img'], width=80)
                with col_txt:
                    st.caption(f"**Briefing from {t['adv']}**")
                    st.info(t['msg'])
                    if st.button("Close Briefing", key=f"close_{task_id}"):
                        st.session_state.briefing_target = None
                        st.rerun()

# --- 6. MAIN UI ---
with st.sidebar:
    st.title(f"🎖️ Level {st.session_state.game_data['level']}")
    titles = ["Junior Associate", "Senior Analyst", "Associate Director", "Partner", "Managing Director", "Chairman"]
    t_idx = min(st.session_state.game_data['level'] - 1, len(titles)-1)
    st.subheader(titles[t_idx])
    
    xp = st.session_state.game_data['xp']
    nxt = st.session_state.game_data['level'] * 500
    prv = (st.session_state.game_data['level'] - 1) * 500
    p_bar = min(max((xp - prv) / (nxt - prv), 0.0), 1.0)
    st.progress(p_bar)
    st.caption(f"{xp} / {nxt} XP to Next Promotion")
    
    st.divider()
    st.metric("Corporate XP", f"{xp:,}")
    st.metric("Isio R&D (RP)", f"{st.session_state.game_data['rp']:,}")

st.title("🏛️ Hungerford Holdings Command")

tabs = st.tabs(["🏛️ Board", "🚨 Critical", "⚡ Ops", "🧹 Maint", "💼 Isio/Capital", "🥂 M&A", "👴 Stake"])

with tabs[0]:
    st.markdown("### 👥 Executive Committee Briefing")
    cols = st.columns(5)
    for i, (name, info) in enumerate(ADVISORS.items()):
        with cols[i]:
            try: st.image(info['img'], use_container_width=True)
            except: st.write("[Asset Missing]")
            st.caption(f"**{name}**")
            st.write(f"_{info['title']}_")
            st.info(info['directive'])

with tabs[1]:
    st.error("### 🚨 Urgent Strategic Priorities")
    urgent_pool = [t for t in DATA_CAPITAL + DATA_STAKE if t.get('urgent') or t.get('xp', 0) >= 150]
    render_command_list(urgent_pool, "crit")

with tabs[2]: render_command_list(DATA_DAILY, "daily")
with tabs[3]: render_command_list(DATA_MAINT, "maint")
with tabs[4]: render_command_list(DATA_ISIO + DATA_CAPITAL, "isiocap")
with tabs[5]: render_command_list(DATA_MA, "ma")
with tabs[6]: render_command_list(DATA_STAKE, "stake")
