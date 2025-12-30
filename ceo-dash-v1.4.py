import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. GLOBAL SETTINGS & STABILITY ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

# --- 2. THE ENGINE: GOOGLE SHEETS & DATA ---
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
    except Exception:
        return None

def load_game_data():
    """Fail-safe loader: Start with Jack's 505 XP baseline if sheet is offline."""
    default_data = {"xp": 505, "rp": 0, "streak": 0, "level": 2}
    try:
        sheet = get_gsheet("Sheet1")
        if sheet:
            row = sheet.row_values(2)
            data = {
                "xp": int(row[1]), 
                "rp": int(row[2]), 
                "streak": int(row[3]), 
                "level": int(row[4])
            }
            if data["xp"] >= 500 and data["level"] == 1:
                data["level"] = 2
            return data
        return default_data
    except Exception:
        return default_data

# --- 3. SESSION STATE INITIALIZATION ---
if 'game_data' not in st.session_state:
    st.session_state.game_data = load_game_data()
if 'active_briefing' not in st.session_state:
    st.session_state.active_briefing = None

def save_game_data(data):
    try:
        sheet1 = get_gsheet("Sheet1")
        if sheet1:
            sheet1.update('B2:E2', [[data['xp'], data['rp'], data['streak'], data['level']]])
            try:
                history_sheet = get_gsheet("XP_History")
                history_sheet.append_row([str(date.today()), data['xp']])
            except: pass
    except: pass

def update_stat(stat, amount, is_urgent=False):
    multiplier = 1.5 if is_urgent else 1.0
    st.session_state.game_data[stat] += int(amount * multiplier)
    # Promotion Check (Level * 500)
    xp_needed = st.session_state.game_data['level'] * 500
    if st.session_state.game_data['xp'] >= xp_needed:
        st.session_state.game_data['level'] += 1
        st.balloons()
    save_game_data(st.session_state.game_data)
    st.rerun()

# --- 4. PERSONNEL & ADVISOR PROFILES ---
ADVISORS = {
    "Chief of Staff": {
        "img": "assets/cos.png", 
        "title": "Strategic Oversight", 
        "directive": "Jack, darling, we need the CCJ cleared today. It is the primary anchor holding back the ship's momentum."
    },
    "Diary Secretary": {
        "img": "assets/diary.png", 
        "title": "Operations & Logistics", 
        "directive": "The Harrow HQ environment is cluttered. Precision in your surroundings dictates precision in your bids."
    },
    "Head of M&A": {
        "img": "assets/m_and_a.png", 
        "title": "Growth & Partnerships", 
        "directive": "You're a high-value asset, handsome. Staying in Harrow is safe, but high-growth happens in the West End."
    },
    "Portfolio Manager": {
        "img": "assets/portfolio.png", 
        "title": "Finance & Treasury", 
        "directive": "The ledger must be balanced. Update the budget tracker today to ensure total liquidity for 2026."
    },
    "Performance Coach": {
        "img": "assets/coach.png", 
        "title": "Human Capital", 
        "directive": "Let's go, Champ! That golf swing needs mobility. 15 minutes of stretching is an investment in power."
    }
}

# --- 5. THE COMPLETE TASK TRANCHE (ALL CSV & MANUAL TASKS) ---
DATA_DAILY = [
    {"name": "Skincare Routine", "xp": 10, "adv": "Chief of Staff", "msg": "The face of the company must remain flawless. Use the SPF."},
    {"name": "Supplement Stack", "xp": 10, "adv": "Performance Coach", "msg": "Fuel your brain, Champ! Omega-3s and Vitamin D for cognitive clarity."},
    {"name": "15 mins stretching", "xp": 15, "adv": "Performance Coach", "msg": "T-spine rotation focus. Let's unlock that backswing."},
    {"name": "Practice Putting ⛳", "xp": 15, "adv": "Performance Coach", "msg": "Consistency over intensity. 20 clean reps."},
    {"name": "Read for 30 mins", "xp": 25, "adv": "Chief of Staff", "msg": "Deep literacy is a competitive advantage. Focus, darling."},
]

DATA_MAINT = [
    {"name": "Laundry Cycle", "xp": 20, "adv": "Diary Secretary", "msg": "A clean uniform for a clean mindset. Zero backlog."},
    {"name": "Clean the Kitchen", "xp": 25, "adv": "Diary Secretary", "msg": "The engine room of the HQ must be spotless."},
    {"name": "Clean the Lounge", "xp": 25, "adv": "Diary Secretary", "msg": "Optimizing the rest area. Clear the clutter."},
    {"name": "Clean the Bathroom", "xp": 30, "adv": "Diary Secretary", "msg": "High-standard hygiene maintenance."},
    {"name": "Remove Shower Mould", "xp": 40, "adv": "Diary Secretary", "msg": "Small fixes prevent structural decay. Do it today."},
]

DATA_CAPITAL = [
    {"name": "Update budget tracker", "xp": 50, "adv": "Portfolio Manager", "msg": "Liquidity is king. Accuracy is the foundation of freedom."},
    {"name": "Plan next week's meals", "xp": 50, "adv": "Performance Coach", "msg": "Fuel planning prevents poor performance. Don't eat like an amateur."},
    {"name": "Reorganise Bedroom", "xp": 80, "adv": "Diary Secretary", "msg": "Your bedroom is your recovery suite. Make it worthy of an executive."},
    {"name": "Review investment portfolio", "xp": 150, "adv": "Portfolio Manager", "msg": "Rebalance assets to ensure inflation-proof growth."},
    {"name": "CCJ: Evidence/Filing", "xp": 200, "urgent": True, "adv": "Portfolio Manager", "msg": "Priority one audit. Ensure every timestamp is recorded."}
]

DATA_ISIO = [
    {"name": "Gov/Client Research", "xp": 40, "adv": "Chief of Staff", "msg": "Information is the primary currency of a bid manager."},
    {"name": "Deep work on CCJ project", "xp": 100, "adv": "Chief of Staff", "msg": "Focus, Jack. 90 minutes of flow will slay this liability."},
    {"name": "Night Owl Session (>8pm)", "rp": 50, "adv": "Diary Secretary", "msg": "I've logged your overtime. Leverage the silence to get ahead."},
    {"name": "Bid/Pursuit Sprint", "rp": 100, "adv": "Chief of Staff", "msg": "Isio's growth depends on this pursuit. Deliver excellence."}
]

DATA_MA = [
    {"name": "Active Networking (Apps)", "xp": 30, "adv": "Head of M&A", "msg": "Keep the pipeline full, handsome. Lead generation never stops."},
    {"name": "Style & Grooming", "xp": 40, "adv": "Head of M&A", "msg": "Packaging is 50% of the sale. Stay sharp."},
    {"name": "Try a new recipe", "xp": 50, "adv": "Performance Coach", "msg": "Culinary skill is a top-tier asset. Learn to cook like a Partner."},
    {"name": "The Date (First Round)", "xp": 100, "adv": "Head of M&A", "msg": "Initial due diligence. Assess her values, not just her LinkedIn."},
    {"name": "Central London Venture", "xp": 150, "adv": "Head of M&A", "msg": "Expand the territory. Break the Harrow bubble this weekend."}
]

DATA_STAKE = [
    {"name": "Arsenal Match Engagement", "xp": 25, "adv": "Diary Secretary", "msg": "Morale is a vital metric. Enjoy the game, MD."},
    {"name": "Weekly Wellness Call (Dad)", "xp": 40, "adv": "Chief of Staff", "msg": "Strategic check-in. His stability is your stability."},
    {"name": "Car Pre-Flight Check", "xp": 40, "adv": "Diary Secretary", "msg": "The CR-V must be mission-ready for the Hungerford run."},
    {"name": "Book Wedding Hotel", "xp": 50, "urgent": True, "adv": "Diary Secretary", "msg": "Secure the lodging today. Social rep is on the line."},
    {"name": "Non-Local Catch-up", "xp": 75, "adv": "Head of M&A", "msg": "Maintain distal connections. Diversify your social portfolio."},
    {"name": "Visit Hungerford", "xp": 150, "adv": "Chief of Staff", "msg": "Presence is the highest-value investment. Oversight of the family asset."}
]

# --- 6. MAIN UI RENDER ---

# Metrics Sidebar
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
    st.caption(f"{xp} / {nxt} XP to Next Rank")
    
    st.divider()
    st.metric("Corporate XP", f"{xp:,}")
    st.metric("Isio R&D (RP)", f"{st.session_state.game_data['rp']:,}")
    if st.button("🔥 Log Daily Streak"): update_stat('streak', 1)

# Body Layout: 70% Tasks, 30% Intelligence Briefing
col_main, col_brief = st.columns([0.7, 0.3])

with col_main:
    st.title("🏛️ Hungerford Holdings Command")
    tabs = st.tabs(["🏛️ Board", "🚨 Critical", "⚡ Ops", "🧹 Maint", "💼 Isio", "🥂 M&A", "👴 Stake"])

    def show_tasks(task_list, key_grp):
        for i, t in enumerate(task_list):
            c1, c2 = st.columns([0.85, 0.15])
            val = t.get('xp', t.get('rp', 0))
            unit = "XP" if 'xp' in t else "RP"
            with c1:
                if st.button(f"{t['name']} (+{val} {unit})", key=f"{key_grp}_{i}", use_container_width=True):
                    update_stat('xp' if 'xp' in t else 'rp', val, is_urgent=t.get('urgent', False))
            with c2:
                if st.button("💬", key=f"chat_{key_grp}_{i}"):
                    st.session_state.active_briefing = t

    with tabs[0]: # Boardroom
        st.markdown("### 👥 Executive Briefing")
        b_cols = st.columns(5)
        for i, (name, info) in enumerate(ADVISORS.items()):
            with b_cols[i]:
                try: st.image(info['img'], use_container_width=True)
                except: st.write("[Asset Missing]")
                st.caption(f"**{name}**")
                st.info(info['directive'])

    with tabs[1]: # Critical Path
        st.error("### 🚨 Urgent Strategic Priorities")
        urgent_pool = [t for t in DATA_CAPITAL + DATA_STAKE if t.get('urgent') or t.get('xp', 0) >= 150]
        show_tasks(urgent_pool, "crit")

    with tabs[2]: show_tasks(DATA_DAILY, "daily")
    with tabs[3]: show_tasks(DATA_MAINT, "maint")
    with tabs[4]: show_tasks(DATA_ISIO + DATA_CAPITAL, "isiocap")
    with tabs[5]: show_tasks(DATA_MA, "ma")
    with tabs[6]: show_tasks(DATA_STAKE, "stake")

# RIGHT COLUMN: THE BRIEFING SUITE
with col_brief:
    st.markdown("### 📞 Intelligence Briefing")
    if st.session_state.active_briefing:
        t = st.session_state.active_briefing
        adv_name = t['adv']
        try: st.image(ADVISORS[adv_name]['img'], width=180)
        except: st.write("[Portrait Missing]")
        st.subheader(adv_name)
        st.info(t['msg'])
        if st.button("Clear Briefing"):
            st.session_state.active_briefing = None
            st.rerun()
    else:
        # Default Chief of Staff View
        try: st.image(ADVISORS["Chief of Staff"]["img"], width=180)
        except: st.write("[CoS Portrait Missing]")
        st.subheader("Chief of Staff")
        st.write("*Standing by for your directives, Jack. Select a tactical icon (💬) to receive a specific memo.*")
        st.divider()
        st.caption(f"Strategy: Today is {date.today().strftime('%A')}. The Holdings expect maximum output.")
