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
        data = {"xp": int(row[1]), "rp": int(row[2]), "streak": int(row[3]), "social_rep": int(row[4]), "level": int(row[5])}
        # Auto-promote to Level 2 based on your 505 XP
        if data["xp"] >= 500 and data["level"] == 1: data["level"] = 2
        return data
    except:
        return {"xp": 505, "rp": 0, "streak": 0, "social_rep": 0, "level": 2}

def save_game_data(data):
    try:
        sheet1 = get_gsheet("Sheet1")
        sheet1.update('B2:F2', [[data['xp'], data['rp'], data['streak'], data['social_rep'], data['level']]])
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

# Sidebar
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
    st.metric("Corporate XP", st.session_state.game_data['xp'])
    st.metric("R&D Points (RP)", st.session_state.game_data['rp'])
    st.metric("Social Rep", st.session_state.game_data['social_rep'])

# --- MASTER TASK LISTS ---
# Sorted by XP (lowest to highest) as requested
daily_ops = sorted([
    {"name": "15 mins stretching", "xp": 10},
    {"name": "Skincare Routine", "xp": 10},
    {"name": "Supplement Stack", "xp": 10},
    {"name": "Practice the Perfect Putt ⛳", "xp": 15},
    {"name": "Read for 30 mins", "xp": 25},
], key=lambda x: x['xp'])

property_maint = sorted([
    {"name": "Laundry Cycle", "xp": 20},
    {"name": "Clean the Kitchen", "xp": 25},
    {"name": "Clean the Lounge", "xp": 25},
    {"name": "Clean the Bathroom", "xp": 30},
    {"name": "Remove Shower Mould", "xp": 40},
], key=lambda x: x['xp'])

capital_projects = sorted([
    {"name": "Gov/Client Research", "xp": 40},
    {"name": "Update budget tracker", "xp": 50},
    {"name": "Plan next week's meals", "xp": 50},
    {"name": "Reorganise Bedroom", "xp": 80},
    {"name": "Re-do the Lounge (Renovation)", "xp": 100},
    {"name": "Review investment portfolio", "xp": 150},
    {"name": "CCJ: Evidence/Filing", "xp": 200, "urgent": True},
], key=lambda x: x['xp'])

m_a_tasks = sorted([
    {"name": "Active Networking (Apps)", "xp": 30},
    {"name": "Personal Presentation (Grooming)", "xp": 40},
    {"name": "Try a new recipe", "xp": 50},
    {"name": "First Round Interview (The Date)", "xp": 100},
    {"name": "Central London Venture (Out of Harrow)", "xp": 150},
], key=lambda x: x['xp'])

stakeholders = sorted([
    {"name": "Arsenal Match Engagement", "xp": 25},
    {"name": "Harrow Catch-up", "xp": 30},
    {"name": "CR-V Market Search", "xp": 40},
    {"name": "Car Pre-Flight Check", "xp": 40},
    {"name": "Weekly Wellness Call (Dad)", "xp": 40},
    {"name": "Book Wedding Hotel", "xp": 50, "urgent": True},
    {"name": "Non-Local Catch-up", "xp": 75},
    {"name": "Visit Hungerford", "xp": 150},
], key=lambda x: x['xp'])

# DASHBOARD
st.title("🏛️ Hungerford Holdings: Strategic Operations")

# New Tab structure with "Critical Path" at the start
tabs = st.tabs(["🚨 Critical Path", "⚡ Daily Ops", "💼 Capital Projects", "🥂 M&A", "👴 Stakeholders"])

# TAB 0: CRITICAL PATH (The "Pressing" View)
with tabs[0]:
    st.error("### Immediate Strategic Objectives")
    st.write("These tasks are time-sensitive or carry high XP impact.")
    
    # Filter for urgent tasks or high XP tasks (>100)
    urgent_tasks = [t for t in capital_projects + stakeholders if t.get('urgent') or t['xp'] >= 150]
    
    for t in urgent_tasks:
        stat_type = 'social_rep' if 'Wedding' in t['name'] else 'xp'
        if st.button(f"CRITICAL: {t['name']} (+{t['xp']} {stat_type.upper()})", key=f"crit_{t['name']}"):
            update_stat(stat_type, t['xp'], is_urgent=True)
            
    st.info("💡 Tip: Use your Night Owl energy to tackle one of these before 11 PM.")

# TAB 1: DAILY OPS
with tabs[1]:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🧘 Operational Readiness")
        for t in daily_ops:
            if st.button(f"{t['name']} (+{t['xp']} XP)", key=f"daily_{t['name']}"):
                update_stat('xp', t['xp'])
    with c2:
        st.markdown("### 🧹 Property Maintenance")
        for t in property_maint:
            if st.button(f"{t['name']} (+{t['xp']} XP)", key=f"prop_{t['name']}"):
                update_stat('xp', t['xp'])

# TAB 2: CAPITAL PROJECTS
with tabs[2]:
    st.markdown("### 🚀 Isio & Major Assets")
    if st.button("Deep work on CCJ project (+100 XP)", key="ccj_deep"): update_stat('xp', 100)
    if st.button("Bid/Pursuit Sprint (+100 RP)", key="isio_p"): update_stat('rp', 100)
    if st.button("Night Owl Session (>8pm) (+50 RP)", key="isio_l"): update_stat('rp', 50)
    st.divider()
    for t in capital_projects:
        if st.button(f"{t['name']} (+{t['xp']} XP)", key=f"cap_{t['name']}"):
            update_stat('xp', t['xp'], is_urgent=t.get('urgent', False))

# TAB 3: M&A
with tabs[3]:
    st.markdown("### 🥂 Mergers & Acquisitions")
    for t in m_a_tasks:
        if st.button(f"{t['name']} (+{t['xp']} XP)", key=f"ma_{t['name']}"):
            update_stat('xp', t['xp'])

# TAB 4: STAKEHOLDERS
with tabs[4]:
    st.markdown("### 👴 Stakeholder Management")
    for t in stakeholders:
        stat = 'social_rep' if 'Catch-up' in t['name'] or 'Wedding' in t['name'] else 'xp'
        if st.button(f"{t['name']} (+{t['xp']} {stat.upper()})", key=f"stake_{t['name']}"):
            update_stat(stat, t['xp'], is_urgent=t.get('urgent', False))
