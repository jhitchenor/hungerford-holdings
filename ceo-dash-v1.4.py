import streamlit as st
import json
import os
from datetime import datetime, date

SAVE_FILE = "ceo_save_game.json"

# --- CORE ENGINE ---
def load_data():
    defaults = {"xp": 0, "rp": 0, "streak": 0, "social_rep": 0, "level": 1}
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            for k, v in defaults.items():
                if k not in data: data[k] = v
            return data
    return defaults

def save_data(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

if 'game_data' not in st.session_state:
    st.session_state.game_data = load_data()

def update_stat(stat, amount, is_urgent=False):
    multiplier = 1.5 if is_urgent else 1.0
    final_amount = int(amount * multiplier)
    st.session_state.game_data[stat] += final_amount
    
    # Level Up Logic (Every 500 XP)
    new_level = (st.session_state.game_data['xp'] // 500) + 1
    if new_level > st.session_state.game_data['level']:
        st.session_state.game_data['level'] = new_level
        st.balloons()
        st.success(f"🎊 LEVEL UP! You are now Level {new_level} CEO")
        
    save_data(st.session_state.game_data)
    st.toast(f"📈 {stat.upper()} +{final_amount} (Urgency Bonus: x{multiplier})")

# --- UI SETUP ---
st.set_page_config(page_title="Hungerford Holdings CEO", layout="wide")

# --- SIDEBAR: TECH TREE & PROGRESS ---
with st.sidebar:
    st.title(f"🎖️ Level {st.session_state.game_data['level']} CEO")
    
    # Progress to Next Level
    current_xp = st.session_state.game_data['xp']
    next_level_xp = st.session_state.game_data['level'] * 500
    prev_level_xp = (st.session_state.game_data['level'] - 1) * 500
    progress = (current_xp - prev_level_xp) / 500
    
    st.write("Level Progress")
    st.progress(min(progress, 1.0))
    st.caption(f"{current_xp} / {next_level_xp} XP")

    st.divider()
    st.subheader("🌲 The Tech Tree")
    st.caption("Unlock new tiers by gaining RP")
    
    # Visual Tech Tree nodes
    tiers = {
        "Tier 1: Survival": 0,
        "Tier 2: Optimization": 250,
        "Tier 3: Automation (Taylor)": 750,
        "Tier 4: Wealth Legacy": 1500
    }
    for tier, req in tiers.items():
        color = "🟢" if st.session_state.game_data['rp'] >= req else "⚪"
        st.write(f"{color} {tier}")

# --- MAIN DASHBOARD ---
st.title("🏛️ Hungerford Holdings: Strategic Ops")
today = date.today()

# --- DYNAMIC CALENDAR MISSIONS ---
st.subheader("📅 Active Missions & Urgency Bonuses")
col_cal1, col_cal2 = st.columns(2)

with col_cal1:
    # Mission 1: The Wedding Booking
    wedding_deadline = date(2025, 12, 23) # Example deadline
    days_left = (wedding_deadline - today).days
    if st.button(f"🏨 Book Krishan's Wedding Hotel ({days_left}d left! 1.5x Bonus)"):
        update_stat('social_rep', 40, is_urgent=True)

with col_cal2:
    # Mission 2: Flat Tidying (Before Dad's)
    if st.button("🧹 Deep Clean Flat (Pre-Holiday Deployment! 1.5x Bonus)"):
        update_stat('xp', 50, is_urgent=True)

st.divider()

t1, t2, t3, t4 = st.tabs(["Daily Maintenance", "Isio & Finance", "Stakeholder: Dad", "Social & Recovery"])

with t1:
    if st.button("✅ 10x Press-ups/Chin-ups"): update_stat('xp', 20)
    if st.button("✅ Skincare/Hygiene Stack"): update_stat('xp', 10)

with t2:
    c1, c2 = st.columns(2)
    with c1:
        st.write("### Work (RP focus)")
        if st.button("🚀 Deploy Project Taylor Sprint"): update_stat('rp', 60)
        if st.button("📋 RFP Automation Testing"): update_stat('rp', 50)
    with c2:
        st.write("### Finance (XP focus)")
        if st.button("💰 Execute ISA/Crypto Rebalance"): update_stat('xp', 40)
        if st.button("📄 Prepare IFA Trust Documents"): update_stat('xp', 60)

with t3:
    st.write("### Supporting Dad")
    if st.button("🚗 Car Research / Showroom Visit"): update_stat('xp', 50)
    if st.button("🩺 Doctor's Appointment 'Success'"): update_stat('xp', 100) # Big reward for hard task!
    if st.button("🎿 2026 Trip / Skiing Research"): update_stat('xp', 30)

with t4:
    if st.button("🏇 Organize Go-Karting/Poker"): update_stat('social_rep', 70)
    if st.button("📖 Read Economist (Anti-Reddit Buff)"): update_stat('xp', 20)
    if st.button("🐎 Watch Slow Horses"): update_stat('xp', 10)