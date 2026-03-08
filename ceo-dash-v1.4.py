import streamlit as st
import gspread
import pandas as pd
import google.generativeai as genai
from datetime import datetime, date
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONFIGURATION & API SETUP ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def get_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("your_key_file.json", scope)
    client = gspread.authorize(creds)
    return client.open("Hungerford_Holdings_Data")

def get_calendar_service():
    # Note: Requires a credentials.json file from Google Cloud Console
    # For this implementation, we use service account logic
    scope = ['https://www.googleapis.com/auth/calendar']
    creds = ServiceAccountCredentials.from_json_keyfile_name("your_key_file.json", scope)
    return build('calendar', 'v3', credentials=creds)

# --- 2. ADVISOR BRAIN (Gemini Integration) ---
def get_advisor_advice(advisor_name, task_name, history_context):
    prompt = f"""
    You are the {advisor_name} for 'Hungerford Holdings', a high-stakes family office. 
    Your MD, Jack, is looking at the task: '{task_name}'.
    Based on his recent history: {history_context}, 
    give a 2-sentence executive briefing. Be professional, demanding of excellence, and concise.
    """
    response = model.generate_content(prompt)
    return response.text

# --- 3. SOVEREIGN DATA ENGINE ---
def load_sovereign_data():
    wb = get_google_sheets()
    stats = wb.worksheet("Sheet1").get_all_records()[0]
    tasks = pd.DataFrame(wb.worksheet("Database").get_all_records())
    red_box = wb.worksheet("Red_Box").get_all_records()
    return stats, tasks, red_box

# --- 4. THE UI COMMAND CENTER ---
st.set_page_config(page_title="HH Executive Command", layout="wide", initial_sidebar_state="collapsed")

def main():
    # CSS for high-impact visual identity
    st.markdown("""
        <style>
        .stButton>button { background: rgba(255, 255, 255, 0.05); border: 1px solid #30363d; height: 100px; }
        .advisor-card { border: 1px solid #58a6ff; padding: 15px; border-radius: 10px; background: #0d1117; }
        .metric-box { font-size: 24px; font-weight: bold; color: #58a6ff; }
        </style>
    """, unsafe_allow_html=True)

    stats, tasks, red_box = load_sovereign_data()

    # Sidebar Stats
    with st.sidebar:
        st.image("assets/cos.png")
        st.title(f"Level {stats['Level']} MD")
        st.divider()
        st.metric("Corporate XP", f"{stats['XP']:,}")
        st.metric("Career RP", f"{stats['RP']:,}")
        st.metric("Streak", f"🔥 {stats['Streak']} Days")

    # Main Interface
    t_ops, t_calendar, t_bureau, t_redbox = st.tabs(["🏛️ Operations", "📅 Schedule", "👥 The Bureau", "📮 Red Box"])

    with t_ops:
        st.header("Operational Control")
        categories = tasks['Category'].unique()
        cols = st.columns(len(categories))
        
        for i, cat in enumerate(categories):
            with cols[i]:
                st.subheader(cat)
                cat_tasks = tasks[tasks['Category'] == cat]
                for idx, row in cat_tasks.iterrows():
                    # Multiplier Logic
                    display_xp = row['XP']
                    if row['Urgency Multiplier'] > 0:
                        display_xp = int(row['XP'] * row['Urgency Multiplier'])
                    
                    if st.button(f"{row['Task Name']}\n+{display_xp} XP / +{row['RP']} RP", key=row['Task ID']):
                        # Logic to update Google Sheet would go here
                        st.balloons()
                        st.success(f"Directive '{row['Task Name']}' Executed.")

    with t_calendar:
        st.header("Diary Secretary's View")
        if st.button("Sync with Google Calendar"):
            # Placeholder for calendar fetch logic
            st.info("Fetching calendar data from Hungerford account...")
            # service = get_calendar_service()
            # events = service.events().list(calendarId='primary').execute()
            st.write("Today: 09:00 Isio Standup | 14:00 Governance Deep-dive")

    with t_bureau:
        st.header("The Board of Advisors")
        advisor_list = ["Chief of Staff", "Performance Coach", "Diary Secretary", "Head of M&A", "Portfolio Manager"]
        cols = st.columns(5)
        for i, name in enumerate(advisor_list):
            with cols[i]:
                st.image(f"assets/{name.lower().replace(' ', '_')}.png")
                st.markdown(f"**{name}**")
                if st.button("Get Briefing", key=f"brief_{name}"):
                    with st.spinner("Consulting..."):
                        advice = get_advisor_advice(name, "General Progress", "MD is Level 1, focused on Isio pursuits.")
                        st.info(advice)

    with t_redbox:
        st.header("Strategic Archive")
        # Display Red Box entries in reverse chronological order
        for entry in reversed(red_box):
            with st.container():
                st.markdown(f"**{entry['Date']} | {entry['Originator']} ({entry['Classification']})**")
                st.write(entry['Note'])
                st.divider()

if __name__ == "__main__":
    main()