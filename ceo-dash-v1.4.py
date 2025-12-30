import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# --- 1. GOOGLE SHEETS ENGINE ---
def get_gsheet(sheet_name="Sheet1"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("your_key_file.json", scope)
    client = gspread.authorize(creds)
    SPREADSHEET_ID = "1wZSAKq283Q1xf9FAeMBIw403lpavRRAVLKNntc950Og" 
    return client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)

def load_game_data():
    try:
        sheet = get_gsheet("Sheet1")
        row = sheet.row_values(2)
        # We now only track B:XP, C:RP, D:Streak, E:Level
        data = {"xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]), "level": int(row[4])}
        if data["xp"] >= 500 and data["level"] == 1: data["level"] = 2
        return data
    except:
        return {"xp": 505, "rp": 0, "streak": 0, "level": 2}

def save_game_data(data):
    try:
        sheet1 = get_gsheet("Sheet1")
        # Update columns B through E
        sheet1.update('B2:E2', [[data['xp'], data['rp'], data['streak'], data['level']]])
        history_sheet = get_gsheet("XP_History")
        history_sheet.append_row([str(date.today()), data['xp']])
    except: pass

# --- 2. INITIALIZATION ---
if 'game_data' not in st.session_state:
    st.session_state.game_data = load_game_data()

def update_stat(stat, amount, is_urgent=False):
    multiplier = 1.5 if is_urgent else 1.0
    final_amount = int(amount * multiplier)
    st.session_state.game_data[stat] += final_amount
    xp_needed_for_next = st.session_state.game_data['level'] * 500
    if st.session_state.game_data['xp'] >= xp_needed_for_next:
        st.session_state.game_data['level'] += 1
        st.balloons()
    save_game_data(st.session_state.game_data)
    st.rerun()

# --- 3. UI SETUP ---
st.set_page_config(page_title="Hungerford Holdings MD", layout="wide")

with st.sidebar:
    st.title(f"🎖️ Level {st.session_state.game_data['level']}")
    titles = ["Junior Associate", "Senior Analyst", "Associate Director", "Partner", "Managing Director", "Chairman"]
    title_idx = min(st.session_state.game_data['level'] - 1, len(titles)-1)
    st.subheader(titles[title_idx])
    
    current_xp = st.session_state.game_data['xp']
    next_level_xp = st.session_state.game_data['level'] * 500
    prev_level_xp = (st.session_state.game_data['level'] - 1) * 500
    progress_perc = min(max((current_xp - prev_level_xp) / (next_level_xp - prev_level_xp), 0.0), 1.0)
    
    st.write("Promotion Progress")
    st.progress(progress_perc)
    st.caption(f"{current_xp} / {next_level_xp} XP to next level")
    
    st.divider()
    st.metric("Total Corporate XP", st.session_state.game_data['xp'])
    st.metric("R&D Points (RP)", st.session_state.game_data['rp'])
    if st.button("🔥 Log Streak"): update_stat('streak', 1)

st.title("🏛️ Hungerford Holdings: Strategic Operations")

# --- TASK DATA WITH ADVICE ---
def render_task_button(task_list, key_prefix, is_rp=False):
    sorted_tasks = sorted(task_list, key=lambda x: x['xp'])
    for t in sorted_tasks:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            label = f"{t['name']} (+{t['xp']} {'RP' if is_rp else 'XP'})"
            if st.button(label, key=f"{key_prefix}_{t['name']}", use_container_width=True):
                update_stat('rp' if is_rp else 'xp', t['xp'], is_urgent=t.get('urgent', False))
        with col2:
            if "advice" in t:
                with st.popover("ℹ️"):
                    st.markdown(f"**Chief of Staff Briefing:**\n\n{t['advice']}")

# Task Definitions
daily_ops = [
    {"name": "15 mins stretching", "xp": 10},
    {"name": "Skincare Routine", "xp": 10, "advice": "Consistency is better than intensity. Your future self will thank you for the SPF."},
    {"name": "Supplement Stack", "xp": 10, "advice": "Take with water. Omega-3s and Vitamin D are key for high-stress roles."},
    {"name": "Practice the Perfect Putt ⛳", "xp": 15},
    {"name": "Read for 30 mins", "xp": 25, "advice": "Focus on long-form content. It trains the attention span needed for complex bids."},
]

property_maint = [
    {"name": "Laundry Cycle", "xp": 20},
    {"name": "Clean the Kitchen", "xp": 25},
    {"name": "Clean the Lounge", "xp": 25},
    {"name": "Clean the Bathroom", "xp": 30},
    {"name": "Remove Shower Mould", "xp": 40, "advice": "Use a specialized bleach spray and leave it for 15 mins. Small fix, big visual impact."},
]

capital_projects = [
    {"name": "Update budget tracker", "xp": 50, "advice": "Accuracy in data is the foundation of every good holding company."},
    {"name": "Plan next week's meals", "xp": 50},
    {"name": "Reorganise Bedroom", "xp": 80, "advice": "Your environment dictates your mindset. A clear room is a clear head."},
    {"name": "Re-do the Lounge (Renovation)", "xp": 100},
    {"name": "Review investment portfolio", "xp": 150, "advice": "Look for diversification. Ensure your 'risk-on' assets match your long-term goals."},
    {"name": "CCJ: Evidence/Filing", "xp": 200, "urgent": True, "advice": "Check the 'Date of Judgment' vs 'Date of Notice'. Keep every email in a dedicated folder."},
]

isio_tasks = [
    {"name": "Deep work on CCJ project", "xp": 100, "advice": "Turn off notifications. 90 mins of flow state is worth 8 hours of distracted work."},
    {"name": "Gov/Client Research", "xp": 40},
]

isio_rp = [
    {"name": "Bid/Pursuit Sprint", "xp": 100, "advice": "Focus on the 'Unique Selling Point'—why Isio over the competitors?"},
    {"name": "Night Owl Session (>8pm)", "xp": 50, "advice": "Leverage your natural rhythm, but set a hard 'screens off' time to protect sleep."},
]

m_a_tasks = [
    {"name": "Active Networking (Apps)", "xp": 30, "advice": "Treat it like lead generation. It's a numbers game, but quality of 'lead' matters most."},
    {"name": "Personal Presentation (Grooming)", "xp": 40},
    {"name": "Try a new recipe", "xp": 50, "advice": "Learning to cook well is a high-ROI skill for future domestic partnership."},
    {"name": "First Round Interview (The Date)", "xp": 100, "advice": "Be curious. Ask questions that reveal their values, not just their hobbies."},
    {"name": "Central London Venture (Out of Harrow)", "xp": 150, "advice": "Getting out of your comfort zone geographically helps get you out of it mentally."},
]

stakeholders = [
    {"name": "Arsenal Match Engagement", "xp": 25},
    {"name": "Harrow Catch-up", "xp": 30},
    {"name": "CR-V Market Search", "xp": 40, "advice": "Focus on mileage and full service history. The 5th Gen Hybrid is a solid reliable 'fleet' asset."},
    {"name": "Car Pre-Flight Check", "xp": 40},
    {"name": "Weekly Wellness Call (Dad)", "xp": 40, "advice": "Be patient. Just listening to his day is a major 'Equity' deposit."},
    {"name": "Book Wedding Hotel", "xp": 50, "urgent": True},
    {"name": "Non-Local Catch-up", "xp": 75, "advice": "Maintaining 'Distal Connections' is key for a well-rounded social portfolio."},
    {"name": "Visit Hungerford", "xp": 150, "advice": "Presence is the most valuable gift you can give your father right now."},
]

# TABS
tabs = st.tabs(["🚨 Critical Path", "⚡ Daily Ops", "💼 Capital & Isio", "🥂 M&A", "👴 Stakeholders"])

with tabs[0]:
    st.error("### Immediate Strategic Objectives")
    all_tasks = daily_ops + property_maint + capital_projects + m_a_tasks + stakeholders + isio_tasks
    urgent_items = [t for t in all_tasks if t.get('urgent') or t['xp'] >= 150]
    render_task_button(urgent_items, "crit")

with tabs[1]:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🧘 Operational Readiness")
        render_task_button(daily_ops, "daily")
    with c2:
        st.markdown("### 🧹 Property Maintenance")
        render_task_button(property_maint, "prop")

with tabs[2]:
    st.markdown("### 🚀 Isio & Major Assets")
    render_task_button(isio_tasks, "isio_xp")
    st.divider()
    st.markdown("### 🧪 R&D (Isio Performance)")
    render_task_button(isio_rp, "isio_rp", is_rp=True)
    st.divider()
    st.markdown("### 📈 Strategic Portfolio")
    render_task_button(capital_projects, "cap")

with tabs[3]:
    st.markdown("### 🥂 Mergers & Acquisitions")
    render_task_button(m_a_tasks, "ma")

with tabs[4]:
    st.markdown("### 👴 Stakeholder Management")
    render_task_button(stakeholders, "stake")
