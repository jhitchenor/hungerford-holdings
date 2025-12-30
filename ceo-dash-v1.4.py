import streamlit as st
# ... [Keeping GSheet and Core Logic from v5.2] ...

# --- 4. TASK LIBRARIES (Refined for Year-End) ---
DATA_DAILY = [
    {"name": "Skincare Routine", "xp": 10, "adv": "Chief of Staff", "msg": "Executive presence is maintained daily."},
    {"name": "Supplement Stack", "xp": 10, "adv": "Performance Coach", "msg": "Recovery after football is vital. Focus on Magnesium and Zinc tonight."},
    {"name": "Post-Football Stretch", "xp": 20, "adv": "Performance Coach", "msg": "Flush the lactic acid. We need those glutes firing for the first tee at Hertsmere tomorrow."},
]

DATA_MAINTENANCE = [
    {"name": "Clean Kitchen", "xp": 25, "adv": "Diary Secretary", "msg": "Reset the engine room before the return to work."},
    {"name": "Laundry: Sports Kit Cycle", "xp": 20, "adv": "Diary Secretary", "msg": "Get the football gear out and the golf gear ready."},
]

DATA_CAPITAL = [
    {"name": "Santander DD Audit", "xp": 60, "adv": "Portfolio Manager", "msg": "Scour the Santander statement. Identify what needs to move to Chase."},
    {"name": "CCJ: Readiness Check", "xp": 50, "adv": "Portfolio Manager", "msg": "Verify the creditor's opening hours for Jan 2nd. We strike as soon as they open."},
    {"name": "Isio Readiness: Inbox Audit", "xp": 75, "adv": "Chief of Staff", "msg": "A 30-minute 'recon' of your work inbox to remove Friday morning anxiety."},
]

DATA_MA = [
    {"name": "Visual Asset Audit: 10 Hinge Photos", "xp": 100, "adv": "Head of M&A", "msg": "Tomorrow evening's priority. No LoRA shortcuts—just the best version of Jack."},
    {"name": "Active Networking (Apps)", "xp": 30, "adv": "Head of M&A", "msg": "The market is active over New Year. Stay visible."},
]

DATA_STAKEHOLDERS = [
    {"name": "Hertsmere Golf Engagement (Shivam)", "xp": 100, "adv": "Performance Coach", "msg": "Focus on the Pendulum Putt. Stakeholder equity + Vitality XP."},
    {"name": "Book Wedding Hotel (Krishan)", "xp": 50, "urgent": True, "adv": "Diary Secretary", "msg": "DEADLINE APPROACHING. Secure the room before you head to Hertsmere."},
    {"name": "Arsenal Match Engagement", "xp": 25, "adv": "Diary Secretary", "msg": "Logged. Enjoy the game, Jack!"},
    {"name": "Visit Hungerford", "xp": 150, "adv": "Chief of Staff", "msg": "High-value deployment. Plan this for the upcoming weekend."},
]

# --- 6. UI ---
# [Tabs and render_command_list logic remains the same as v5.2]
# Restored Full Tab Names: 
tabs = st.tabs(["🏛️ Board", "🚨 Critical", "⚡ Ops", "🧹 Maintenance", "💼 Isio/Capital", "🥂 M&A", "👴 Stakeholders"])
