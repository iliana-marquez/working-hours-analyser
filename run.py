import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import holidays
from datetime import datetime, date, timedelta, time
from dateutil.parser import parse
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
    def __init__(self, calendar_id: str, title_filter: Optional[str] = None):
        self.calendar_id = calendar_id
        self.events: List[dict] = []
        self.title_filter = title_filter

    @classmethod
    def from_input(calendar_class):
        """
        Collects and validates the calendar ID from input
        """
        while True:
            calendar_id = input("Please enter the ID of your calendar (e.g., 'primary'):\n>").strip()
            if calendar_id:
                break
            print("Calendar ID cannot be empty. Please enter your calendar ID.\n")
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


class WorkCalendar(Calendar):
    @classmethod
    def from_input(workcal_class):
        """
        To create an instance of WorkCalendar by collecting user input
        including an optional title filter
        (workcal_class not passed into the super().from_input()
        as it will internally use workcal_class)
        """
        calendar = super().from_input()
        title_filter = input("\nEnter a keyword or event title to filter your work events or press enter to skip:\n>").strip() or None
        calendar.title_filter = title_filter
        return calendar

    def fetch_filtered_events(self, start_date, end_date):
        """
        To fetch the period filtered events of this instance
        and filters them by title if requested
        """
        self.fetch_events_by_period(start_date, end_date)
        return self.filter_events_by_title(self.title_filter)

    def get_shifts(self, start_date, end_date, all_day_policy: str = "omit") -> list[dict]:
        """
        Fetches filtered events to return a list of shifts
        with parsed start, end, duration.
        all_day_policy (str): Determines how to handle all-day events
            - "omit" (default): Skip all-day event
            - "8hr": Count all-day events as 8-hour shifts
            - "24hr": Count all-day events as 24-hour shifts
        """
        events = self.fetch_filtered_events(start_date, end_date)
        shifts = []
        for event in events:
            start_info = event.get("start", {})
            end_info = event.get("end", {})
            is_all_day = "date" in start_info and "date" in end_info
            start = start_info.get("dateTime") or start_info.get("date")
            end = end_info.get("dateTime") or end_info.get("date")
            if is_all_day:
                if all_day_policy == "omit":
                    continue
                hours = 8.0 if all_day_policy == "8hr" else 24.0
                shifts.append({
                    "title": event.get("summary", ""),
                    "start": start,
                    "end": end,
                    "duration": hours,
                    "all_day": True
                })
                continue
            try:
                start_time = parse(start)
                end_time = parse(end)
                if end_time <= start_time:
                    continue
                duration = (end_time - start_time).total_seconds() / 3600
            except Exception:
                continue
            shifts.append({
                "title": event.get("summary", ""),
                "start": start_time,
                "end": end_time,
                "duration": duration,
                "all_day": False
                })
        return shifts

    def calculate_worked_hours(self, start_date, end_date, all_day_policy="omit") -> float:
        shifts = self.get_shifts(start_date, end_date, all_day_policy)
        return sum(shift["duration"] for shift in shifts)

    def calculate_worked_days(self, start_date, end_date, all_day_policy: str = "omit") -> int:
        """
        To return the number of unique days with at least one shift worked
        using a set of dates to automatically remove
        duplicate date objects (shift["start"])
        """
        shifts = self.get_shifts(start_date, end_date, all_day_policy)
        worked_days = {shift["start"].date() for shift in shifts}
        return len(worked_days)


def get_calendar_data() -> WorkCalendar:
    """
    To test the Calendar class with user input
    """
    return WorkCalendar.from_input()


class VacationCalendar(Calendar):
    @classmethod
    def from_input(vacationcal_class):
        """
        To create an instance of VacationCalendar by collecting user input
        including an optional title filter
        """
        calendar = super().from_input(vacationcal_class)
        title_filter = input("Enter a keyword or event title to filter vacation events or press Enter to skip:\n>").strip() or None
        calendar.title_filter = title_filter
        return calendar

    def fetch_filtered_events(self, start_date, end_date):
        """
        To fetch the period filtered events of this instance
        and filters them by title if requested
        """
        self.fetch_events_by_period(start_date, end_date, all_day_policy)
        return self.filter_events_by_title(self.title_filter)


def main_testing():
    # print("-------------------------------------------")
    # print("👋 Welcome to the Working Hours Analyser!🔍")
    # print("-------------------------------------------")
    # user = get_user_data()
    # print("\nUser data succesfully collected:")
    # print(f"Name: {user.name}")
    # print(f"Name: {user.weekly_contract_hours}")
    # print(f"Name: {user.country_code}")
    work_calendar = get_calendar_data()
    start = date(2025, 1, 1)
    end = date(2025, 1, 31)
    print(f"\n>>>Fetching events between {start} and {end}...")
    print("-------------------------------------------")
    print("Events")
    print("-------------------------------------------")
    events = work_calendar.fetch_filtered_events(start, end)
    if not events:
        print(f"\n No events found between {start} and {end}.")
    else:
        print(f"\n Found {len(events)} event(s):")
        for event in events:  
            print("•", event.get("summary", "No Title"))
    print("\n-------------------------------------------")
    print("Shifts")
    print("-------------------------------------------")
    shifts = work_calendar.get_shifts(start, end, all_day_policy="8hr")
    for shift in shifts:
        print(f"{shift['title']}: {shift['start']} - {shift['end']} ({shift['duration']})\n")
    print("\n>>> Calculating total worked hours (all-day policy = '8hr')...")
    print("-------------------------------------------")
    total_hours = work_calendar.calculate_worked_hours(start, end, all_day_policy="8hr")
    print(f"Total worked hours: {total_hours:.2f} hrs")
    total_worked_days = work_calendar.calculate_worked_days(start, end, all_day_policy="8hr")
    print(f"Total worked days: {total_worked_days}")
    print("-------------------------------------------\n")


main_testing()