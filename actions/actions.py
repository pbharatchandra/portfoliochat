import json
from typing import Any, Text, Dict, List
from pathlib import Path
import os

import google.generativeai as genai
from dotenv import load_dotenv

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import gspread
from google.oauth2.service_account import Credentials

# --- Load environment variables ---
load_dotenv()
# Add this after load_dotenv() to debug
load_dotenv()
print(f"Gemini API Key present: {bool(os.getenv('AIzaSyAa9Z7LICLKXCx66MBuiLal4CinnWjROFQ'))}")
print(f"Google Project ID: {os.getenv('GOOGLE_PROJECT_ID')}")
# --- In-memory fallback log ---
FALLBACK_LOG: List[Dict[str, str]] = []

# --- Google Sheets configuration using environment variables ---
def get_google_sheets_client():
    """Create Google Sheets client using environment variables"""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Get credentials from environment variables
    credentials_dict = {
        "type": "service_account",
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY", "").replace('\\n', '\n'),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL")
    }
    
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
    return gspread.authorize(credentials)

def log_fallback_to_sheets(user_message: str, sender: str):
    """Log fallbacks directly into Google Sheets"""
    try:
        client = get_google_sheets_client()
        sheet = client.open("rasa-fallbacks").sheet1
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([user_message, sender, timestamp])
    except Exception as e:
        print(f"Error logging to Google Sheets: {e}")

def log_fallback(user_message: str):
    """Log fallback to in-memory storage"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    FALLBACK_LOG.append({
        "message": user_message,
        "timestamp": timestamp
    })

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Course mapping dictionary ---
COURSE_MAPPING = {
    "b.tech": "btech_general", "btech": "btech_general", "bachelors in technology": "btech_general",
    "b.tech (computer science & engineering)": "btech_cse", "computer science & engineering": "btech_cse",
    "b.tech cse": "btech_cse", "cse": "btech_cse",
    "b.tech (information technology)": "btech_it", "information technology": "btech_it",
    "b.tech it": "btech_it", "it": "btech_it",
    "b.tech (cse - artificial intelligence & machine learning)": "btech_cse_ai_ml", "ai & ml": "btech_cse_ai_ml",
    "artificial intelligence": "btech_cse_ai_ml",
    "b.tech (cse - data science)": "btech_cse_ds", "data science": "btech_cse_ds",
    "b.tech (electronics and communication engineering)": "btech_ece", "electronics and communication": "btech_ece",
    "b.tech ece": "btech_ece", "ece": "btech_ece",
    "b.tech (civil engineering)": "btech_civil", "civil engineering": "btech_civil", "civil": "btech_civil",
    "b.tech (electrical engineering)": "btech_ee", "electrical engineering": "btech_ee", "ee": "btech_ee",
    "b.tech (electrical & electronics engineering)": "btech_eee", "electrical & electronics engineering": "btech_eee",
    "eee": "btech_eee",
    "b.tech (mechanical engineering)": "btech_mech", "mechanical engineering": "btech_mech", "mechanical": "btech_mech",
    "bachelor of computer applications": "bca", "bca": "bca",
    "m.sc (physics)": "msc_physics", "msc physics": "msc_physics",
    "m.sc (chemistry)": "msc_chemistry", "msc chemistry": "msc_chemistry",
    "m.sc (mathematics)": "msc_math", "msc mathematics": "msc_math",
    "m.sc (computer science)": "msc_cs", "msc computer science": "msc_cs", "msc cs": "msc_cs",
    "m.sc (data science)": "msc_ds", "msc data science": "msc_ds",
    "m.sc (biotechnology)": "msc_biotech", "msc biotechnology": "msc_biotech",
    "mba": "mba", "mba finance": "mba", "mba hr": "mba", "mba marketing": "mba",
    "master of computer applications": "mca", "mca": "mca",
    "m.tech (computer science and engineering)": "mtech_cse", "m.tech cse": "mtech_cse",
    "m.tech (electronics and communication engineering)": "mtech_ece", "m.tech ece": "mtech_ece",
    "m.tech (vlsi and embedded systems design)": "mtech_vlsi", "m.tech vlsi": "mtech_vlsi", "vlsi": "mtech_vlsi",
    "m.tech (wireless communication technology)": "mtech_wireless", "m.tech wireless": "mtech_wireless",
    "m.tech (construction technology & management)": "mtech_ctm", "m.tech ctm": "mtech_ctm",
    "m.tech (thermal engineering)": "mtech_thermal", "m.tech thermal": "mtech_thermal",
    "phd": "phd"
}

# ------------------------------
# Action to show course info
# ------------------------------
class ActionShowCourseInfo(Action):

    def name(self) -> Text:
        return "action_show_course_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        project_root = Path(__file__).parent.parent
        db_path = project_root / "courses_db.json"

        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                course_db = json.load(f)
        except FileNotFoundError:
            dispatcher.utter_message(text="Error: The courses_db.json file was not found.")
            return []

        course_entity = next(tracker.get_latest_entity_values("course"), None)
        if not course_entity:
            dispatcher.utter_message(text="Which course are you asking about?")
            return []

        normalized_course = course_entity.lower()
        course_key = COURSE_MAPPING.get(normalized_course)

        if course_key and course_key in course_db:
            course_info = course_db[course_key]
            intent = tracker.latest_message['intent'].get('name')
            if intent == 'ask_duration':
                response_text = f"The duration for {course_info.get('name')} is {course_info.get('duration')}."
            elif intent == 'ask_fees':
                response_text = f"The annual fee for {course_info.get('name')} is {course_info.get('fee')}."
            elif intent == 'ask_admission':
                response_text = f"Admission to {course_info.get('name')} is through {course_info.get('admission')}."
            elif intent == 'ask_level':
                response_text = f"{course_info.get('name')} is a {course_info.get('level')} level program."
            else:
                response_text = (
                    f"Here is the information for {course_info.get('name')}:\n"
                    f"- Level: {course_info.get('level')}\n"
                    f"- Duration: {course_info.get('duration')}\n"
                    f"- Admission: {course_info.get('admission')}\n"
                    f"- Annual Fee: {course_info.get('fee')}"
                )
            dispatcher.utter_message(text=response_text)
            return [
                SlotSet("course_name", course_info.get("name")),
                SlotSet("course_duration", course_info.get("duration")),
                SlotSet("course_level", course_info.get("level")),
                SlotSet("course_admission", course_info.get("admission")),
                SlotSet("course_fee", course_info.get("fee"))
            ]
        elif course_key == "btech_general":
            dispatcher.utter_message(text="NIST offers B.Tech in several specializations. Which branch are you interested in?")
            return []
        else:
            dispatcher.utter_message(response="utter_course_not_found")
            return []

# ------------------------------
# Generative fallback action
# ------------------------------
class ActionGenerativeFallback(Action):
    def name(self) -> Text:
        return "action_generative_fallback"
        
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_question = tracker.latest_message.get('text')
        sender_id = tracker.sender_id
        
        # Log to Google Sheets
        log_fallback_to_sheets(user_question, sender_id)
        
        prompt = f"""You are a helpful assistant for NIST University. Answer user questions concisely.
        If unknown, say like, "I'm sorry, I don't have information on that topic." or similar.
        User question: "{user_question}"
        """

        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            dispatcher.utter_message(text=response.text)
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            dispatcher.utter_message(response="utter_nlu_fallback")
            log_fallback(user_question)  # log the fallback

        return []