import streamlit as st
# ... [Keeping original GSheet and State logic from v5.0] ...

# --- NEW: THE TREASURY SHOP DATA ---
REWARDS = [
    {"name": "PS5 Controller", "cost": 350, "adv": "Portfolio Manager"},
    {"name": "Second Hand 7-Wood", "cost": 800, "adv": "Performance Coach"},
    {"name": "65\" 4K TV", "cost": 2500, "adv": "Diary Secretary"},
    {"name": "Dubai Trip (Ash & Nick)", "cost": 6000, "adv": "Head of M&A"},
]

# --- NEW: FINANCIAL & M&A TASKS ---
DATA_FINANCE = [
    {"name": "Audit Santander Direct Debits", "xp": 60, "adv": "Portfolio Manager", "msg": "Identify every 'Legacy DD' and move them to Chase. Efficiency is profit."},
    {"name": "Close Santander Account", "xp": 100, "adv": "Portfolio Manager", "msg": "Liquidate the relic. One less point of failure in our system."},
    {"name": "Apply for Credit Builder Card", "xp": 80, "adv": "Portfolio Manager", "msg": "We need to show the market we are a reliable borrower. Use it for fuel only."},
    {"name": "Bitcoin/Gold Allocation (Initial)", "xp": 150, "adv": "Portfolio Manager", "msg": "Diversifying the Holdings into hard assets. HODL starts here."},
]

DATA_MA_EXPANDED = [
    {"name": "Intimacy Strategy Briefing", "xp": 50, "adv": "Chief of Staff", "msg": "Jack, darling, let's have a glass of wine and look at the pros/cons of your intimacy plan. We act with intention, not impulse."},
    {"name": "Marylebone Evening Scout", "xp": 150, "adv": "Head of M&A", "msg": "Let's put you in a high-value environment. Marylebone is sophisticated, just like the partner you deserve."},
]

# --- UPDATED TAB LOGIC ---
# Inside your tabs list:
tabs = st.tabs(["🏛️ Board", "🚨 Critical", "⚡ Ops", "💼 Finance", "💼 Isio/Capital", "🥂 M&A", "👴 Stakeholders", "💎 Shop"])

with tabs[3]:
    st.subheader("📈 The Treasury: Financial Consolidation")
    render_command_list(DATA_FINANCE, "fin")

with tabs[5]:
    st.subheader("🥂 Mergers & Acquisitions")
    render_command_list(DATA_MA + DATA_MA_EXPANDED, "ma")

with tabs[7]:
    st.header("💎 The Reward Shop")
    st.write(f"Treasury Balance: **{st.session_state.game_data['credits']} CC**")
    
    for r in REWARDS:
        can_afford = st.session_state.game_data['credits'] >= r['cost']
        if st.button(f"CLAIM: {r['name']} ({r['cost']} CC)", disabled=not can_afford, use_container_width=True):
            st.session_state.game_data['credits'] -= r['cost']
            st.balloons()
            st.success(f"MD, you have earned the {r['name']}. Permission to spend real capital granted.")
            st.rerun()
