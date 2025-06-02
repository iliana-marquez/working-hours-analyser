import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import holidays
from datetime import datetime, date, timedelta, time
from typing import Optional, List

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar.readonly"
]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPE_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPE_CREDS)
SHEET = GSPREAD_CLIENT.open('working-hours-reports')
CALENDAR_SERVICE = build('calendar', 'v3', credentials=SCOPE_CREDS)


class User:
    def __init__(self, name: str, weekly_contract_hours: float, country_code: str):
        self.name = name
        self.weekly_contract_hours = weekly_contract_hours
        self.country_code = country_code.upper()

    @classmethod
    def from_input(user_class):
        """
        Gathers and validates the user information from inputs
        """
        while True:
            name = input("What is your name?\n>").strip()
            if name:
                break
            print("Please type your name:\n>")
        while True:
            hours_input = input("What are your weekly contract hours (e.g., 26.5)?\n> ")
            try:
                weekly_contract_hours = float(hours_input)
                break
            except ValueError:
                print("Please enter a valid number (e.g., 26.5) for calculations:\n> ")
        while True:
            country_code = input("Please enter your country's two-letter code (e.g., 'AT' for Austria):\n> ").strip()
            if len(country_code) == 2 and country_code.isalpha():
                break
            print("Your country code must be exactly two letters, please try again:\n> ")

        return user_class(name, weekly_contract_hours, country_code)


def get_user_data() -> User:
    """
    to test the gathering and validation
    """
    return User.from_input()


class Calendar:
    def __init__(self, calendar_id: str):
        self.calendar_id = calendar_id
        self.events: List[dict] = []

    @classmethod
    def from_input(calendar_class):
        """
        Collects and validates the calendar ID from input
        """
        while True:
            calendar_id = input("Please enter the ID of your work calendar (e.g., 'primary'):\n>").strip()
            if calendar_id:
                break
            print("Please enter your calendar ID:\n")
        return calendar_class(calendar_id)

    def fetch_events_by_period(self, start_date: date, end_date: date) -> List[dict]:
        """
        Fetches events from the calendar using its ID 
        within a given period of time.
        """
        try:
            time_min = datetime.combine(start_date, time.min).isoformat() + 'Z'
            time_max = datetime.combine(end_date, time.max).isoformat() + 'Z'

            events_result = CALENDAR_SERVICE.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            self.events = events_result.get('items') or []
        except Exception as e:
            print(f"Error fetching events: {e}")
        return self.events

    def filter_events_by_title(self, title_filter: Optional[str] = None) -> List[dict]:
        """
        Filters events by title keyword if provided
        (not casesensitive)
        """
        if not title_filter:
            return self.events

        filtered_events = [
            event for event in self.events
            if title_filter.lower() in event.get("summary", "").lower()
        ]
        return filtered_events
    
def get_calendar_data() -> Calendar:
    """
    To test the Calendar class with user input
    """
    return Calendar.from_input()


def main():
    print("------------------------------------------")
    print("👋  Welcome to the Working Hours Analyser!")
    print("------------------------------------------")
    user = get_user_data()
    print("\nUser data succesfully collected:")
    print(f"Name: {user.name}")
    print(f"Name: {user.weekly_contract_hours}")
    print(f"Name: {user.country_code}")
    calendar = get_calendar_data()
    start = date(2025, 1, 1)
    end = date(2025, 1, 31)
    print(f"\n📅 Fetching events between {start} and {end}...")
    events = calendar.fetch_events_by_period(start, end)
    if not events:
        print(f"\n⚠️ No events found between {start} and {end}.")
    else:
        print(f"\n Found {len(events)} event(s). Sample titles:")
        for event in events[:5]:  #just a few for testing
            print("•", event.get("summary", "No Title"))
    keyword = input("\n🔍 Enter keyword to filter events (or leave blank):\n> ").strip()
    filtered = calendar.filter_events_by_title(keyword)
    print(f"\n🎯 Events after filtering ({len(filtered)}):")
    for event in filtered:
        print("•", event.get("summary", "No Title"))


main()


