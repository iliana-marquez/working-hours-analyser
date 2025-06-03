import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import holidays
from datetime import datetime, date, timedelta, time
from dateutil.parser import parse
from typing import Optional, List, Dict, Set
import re

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

WEEKDAYS_ORDERED = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

WEEKDAY_ALIASES = {
    'mo': 'mon', 'mon': 'mon', 'monday': 'mon',
    'tu': 'tue', 'tue': 'tue', 'tuesday': 'tue',
    'we': 'wed', 'wed': 'wed', 'wednesday': 'wed',
    'th': 'thu', 'thu': 'thu', 'thursday': 'thu',
    'fr': 'fri', 'fri': 'fri', 'friday': 'fri',
    'sa': 'sat', 'sat': 'sat', 'saturday': 'sat',
    'su': 'sun', 'sun': 'sun', 'sunday': 'sun',
}


class User:
    def __init__(self, name: str, country_code: str,  weekly_contract_hours: float, contract_working_weekdays: List[str]):
        self.name = name
        self.country_code = country_code.upper()
        self.weekly_contract_hours = weekly_contract_hours
        self.contract_working_weekdays = contract_working_weekdays

    @classmethod
    def from_input(user_class):
        """
        Gathers and validates the user information from inputs
        """
        while True:
            name = input("What is your name?\n> ").strip()
            if name:
                break
            print("Please type your name.")
        while True:
            country_code = input("Please enter your country's two-letter code (e.g., 'AT' for Austria):\n> ").strip()
            if len(country_code) == 2 and country_code.isalpha():
                break
            print("Your country code must be exactly two letters, please try again.")
        while True:
            hours_input = input("What are your weekly contract hours (e.g., 26.5)?\n> ").strip()
            try:
                weekly_contract_hours = float(hours_input)
                break
            except ValueError:
                print("Please enter a valid number (e.g., 26.5) for calculations.")

        contract_working_weekdays =  user_class.get_contract_working_weekdays()

        return user_class(name, country_code, weekly_contract_hours, contract_working_weekdays)
    
    @staticmethod
    def get_contract_working_weekdays() -> List[int]:
        """
        To collect the user's specific contract working weekdays
        """
        print("\nWhat is your standard working week?")
        print("-------------------------------------------")
        print("1. Mon-Fri")
        print("2. Mon-Sat")
        print("3. Mon-Thu")
        print("4. Flexible (Every day)")
        print("5. Custom (Other specific days or range)")
        print("-------------------------------------------")
        while True:
            choice = input("Type the selected option number:\n> ").strip()
            if choice == '1':
                return list(range(0, 5)) 
            elif choice == '2':
                return list(range(0, 6))
            elif choice == '3':
                return list(range(0, 4))
            elif choice == '4':
                return list(range(0, 7))
            elif choice == '5':
                return User._custom_working_weekdays_input()
            else:
                print("Please choose a valid option from 1 to 5).")

    @staticmethod
    def _custom_working_weekdays_input() -> List[str]:
        """
        To transform the custom input into clean and valid output for
        get_contract_working_weekdays():
        - Mixed input: Ranges and individual days (e.g. mon-th sa or mo - we sun)
        - Orders by weekday
        """
        print("\nEnter your working days (mon, tue, wed, thu, fri, sat, sun):")
        print("------------------------------------------------------------")
        print("You can enter either or both, depending on your contract:")
        print(" • A range of days (e.g. Mon-Fri or Fri-Mon)")
        print(" • A list of specific days (e.g. Mon Tue Fri)")
        print("------------------------------------------------------------")
        while True:
            user_input = input("> ").lower().strip()
            normalized = user_input.replace(',', ' ')
            normalized = re.sub(r'[–—-]', '-', normalized)
            normalized = re.sub(r'\s*-\s*', '-', normalized)
            entries = normalized.split()
            all_valid = True
            selected_days = []
            for entry in entries:
                if '-' in entry:
                    parts = entry.split('-')
                    if len(parts) != 2:
                        all_valid = False
                        break
                    start = WEEKDAY_ALIASES.get(parts[0])
                    end = WEEKDAY_ALIASES.get(parts[1])
                    if not start or not end:
                        all_valid = False
                        break
                    start_index = WEEKDAYS_ORDERED.index(start)
                    end_index = WEEKDAYS_ORDERED.index(end)
                    if start_index <= end_index:
                        selected_days.extend(range(start_index, end_index + 1))
                    else:
                        selected_days.extend(list(range(start_index, 7)) + list(range(0, end_index + 1)))
                else:
                    entry_clean = entry.lower().strip()
                    day = WEEKDAY_ALIASES.get(entry_clean)
                    if not day:
                        all_valid = False
                        break
                    day_index = WEEKDAYS_ORDERED.index(day)
                    selected_days.append(day_index)

            if not all_valid:
                print("Invalid day or range detected. Please use correct day names or ranges (e.g., 'mon', 'wed-fri'). Try again.")
                continue

            seen = set()
            unique_days = [d for d in range(7) if d in selected_days and not (d in seen or seen.add(d))]
            if unique_days:
                return unique_days
            print("Invalid format. Try again using day names (e.g ''Mon Wed Fri') and/or ranges (e.g Wed-Fri)")

    def get_contract_working_weekdays_dates(self, start_date: date, end_date: date) -> Set[date]:
        """
        Return the set of dates between start_date and end_date that fall on contract working weekdays.
        Used to filter holidays that actually fall on working days.
        """
        all_days = (end_date - start_date).days + 1
        return {
            start_date + timedelta(days=i)
            for i in range(all_days)
            if (start_date + timedelta(days=i)).weekday() in self.contract_working_weekdays
        }


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
            calendar_id = input("\nPlease enter the ID of your calendar (e.g., 'primary'):\n> ").strip()
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
            expanded_start = start_date - timedelta(days=1)
            time_min = datetime.combine(expanded_start, time.min).isoformat() + 'Z'
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
        title_filter = input("\nEnter a keyword or event title to filter your work events or press enter to skip:\n> ").strip() or None
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
        that fall within the [start_date, end_date] range
        with parsed start, end, duration.
        all_day_policy (str): Determines how to handle all-day events
            - "omit" (default): Skip all-day event
            - "8hr": Count all-day events as 8-hour shifts
            - "24hr": Count all-day events as 24-hour shifts
        """
        range_start = datetime.combine(start_date, time.min)
        range_end = datetime.combine(end_date, time.max)
        events = self.fetch_filtered_events(range_start, range_end)
        shifts = []
        for event in events:
            start_info = event.get("start", {})
            end_info = event.get("end", {})
            is_all_day = "date" in start_info and "date" in end_info
            shift_raw_start = start_info.get("dateTime") or start_info.get("date")
            shift_raw_end = end_info.get("dateTime") or end_info.get("date")
            if is_all_day:
                if all_day_policy == "omit":
                    continue
                hours = 8.0 if all_day_policy == "8hr" else 24.0
                shifts.append({
                    "title": event.get("summary", ""),
                    "start": shift_raw_start,
                    "end": shift_raw_end,
                    "duration": hours,
                    "all_day": True
                })
                continue
            try:
                shift_start = parse(shift_raw_start).replace(tzinfo=None)
                shift_end = parse(shift_raw_end).replace(tzinfo=None)
                if shift_end <= shift_start:
                    continue
            except Exception:
                continue
            if shift_end <= range_start or shift_start >= range_end:
                continue
            clipped_start = max(shift_start, range_start)
            clipped_end = min(shift_end, range_end)
            duration = (clipped_end - clipped_start).total_seconds() / 3600
            shifts.append({
                "title": event.get("summary", ""),
                "start": clipped_start,
                "end": clipped_end,
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
        print("\nNow your vacation calendar")
        calendar = super().from_input()
        title_filter = input("\nEnter a keyword or event title to filter your vacation events or press Enter to skip:\n> ").strip() or None
        calendar.title_filter = title_filter
        return calendar

    def fetch_filtered_events(self, start_date, end_date):
        """
        To fetch the period filtered events of this instance
        and filters them by title if requested
        """
        self.fetch_events_by_period(start_date, end_date)
        return self.filter_events_by_title(self.title_filter)

    def get_vacation_days(self, start_date: date, end_date: date) -> set:
        """
        To calculate the number of vacation days between start_date and end_date,
        from filtered events, clipping any multi-day events to stay within bounds.
        clipped_start = max(date_start, start_date) - clip up to start_date if event starts earlier
        clipped_end = min(date_end, end_date) - clip down to end_date if event ends later
        """
        vacation_events = self.fetch_filtered_events(start_date, end_date)
        vacation_days = set()
        for vacation_event in vacation_events:
            start_info = vacation_event.get("start", {})
            end_info = vacation_event.get("end", {})
            start_str = start_info.get("dateTime") or start_info.get("date")
            end_str = end_info.get("dateTime") or end_info.get("date")
            try:
                date_start = parse(start_str).date()
                date_end = parse(end_str).date()
                if "date" in start_info and "date" in end_info:
                    date_end -= timedelta(days=1)
                clipped_start = max(date_start, start_date)
                clipped_end = min(date_end, end_date)
                if clipped_start <= clipped_end:
                    for single_day in range((clipped_end - clipped_start).days + 1):
                        day = clipped_start + timedelta(days=single_day)
                        vacation_days.add(day)
            except Exception as e:
                print(f"Skipping event due to error: {e}")
        return vacation_days

    def calculate_vacation_days(self, start_date: date, end_date: date) -> int:
        vacation_days = self.get_vacation_days(start_date, end_date)
        return len(vacation_days)


def get_vacation_calendar() -> VacationCalendar:
    """
    To test the VacationCalendar class
    """
    return VacationCalendar.from_input()


class HolidayCalendar:
    def __init__(self, country_code: str):
        self.country_code = country_code
        self.holidays: List[Dict[str, date]] = []

    def fetch_holidays(self, start_date: date, end_date: date) -> List[Dict[str, any]]:
        """
        To fetch the official public holidays between start_date and 
        end_date for the given country
        """
        all_holidays = holidays.country_holidays(self.country_code)
        included_day = start_date
        self.holidays = []
        while included_day <= end_date:
            if included_day in all_holidays:
                self.holidays.append({
                    "date": included_day,
                    "title": all_holidays[included_day]
                })
            included_day += timedelta(days=1)
        return self.holidays
    
    def count_holidays(self) -> int:
        return len(self.holidays)


def get_holiday_calendar(country_code) -> HolidayCalendar:
    """
    To test the holidaycalendar class with user input
    """
    return HolidayCalendar(country_code)


class Report:
    def __init__(
            self,
            user: 'User',
            work_calendar: 'WorkCalendar',
            vacation_calendar: 'VacationCalendar',
            holiday_calendar: 'HolidayCalendar',
            start_date: date,
            end_date: date,
            all_day_policy: str = "omit"
    ):
        self.user = user
        self.work_calendar = work_calendar
        self.vacation_calendar = vacation_calendar
        self.holiday_calendar = holiday_calendar
        self.start_date = start_date
        self.end_date = end_date
        self.all_day_policy = all_day_policy
        # Fetch events and holidays once for the period
        self.work_calendar.fetch_filtered_events(start_date, end_date)
        self.vacation_calendar.fetch_filtered_events(start_date, end_date)
        self.holiday_calendar.fetch_holidays(start_date, end_date)
        # Get sets of vacation and holiday days
        self.vacation_days: Set[date] = self.vacation_calendar.get_vacation_days(start_date, end_date)
        self.holiday_days: Set[date] = {h['date'] for h in self.holiday_calendar.holidays}
        # Calculate overlapping holiday days within vacation days
        self.overlapping_days: Set[date] = self.vacation_days & self.holiday_days
        # Adjust vacation days by removing overlapping holidays
        self.adjusted_vacation_days: Set[date] = self.vacation_days - self.overlapping_days
        # FIXED: Only count holidays that are working days AND not overlapping with vacation
        contract_workdays = self.user.get_contract_working_weekdays_dates(start_date, end_date)
        self.adjusted_holiday_days: Set[date] = {
            day for day in self.holiday_days
            if day in contract_workdays and day not in self.vacation_days
        }

    def calculate_expected_working_days(self) -> int:
        """
        To return working days that are not vacation or holiday days.
        """
        all_days = (self.end_date - self.start_date).days + 1
        expected_days = 0
        for i in range(all_days):
            current_day = self.start_date + timedelta(days=i)
            weekday = current_day.weekday()
            if weekday in self.user.contract_working_weekdays:
                if current_day not in self.adjusted_holiday_days and current_day not in self.adjusted_vacation_days:
                    expected_days += 1
        return expected_days
    
    def calculate_vacation_days_count(self) -> int:
        """
        To return the count of vacation days after subtracting overlapping holidays
        """
        return len(self.adjusted_vacation_days)
    
    def calculate_holiday_days_count(self) -> int:
        """
        To return the count of all holidays in the period that fall on working days
        """
        return len(self.adjusted_holiday_days)

    def calculate_total_days_off(self) -> int:
        """
        Total days off = vacation days (adjusted) + all holidays (including overlapping)
        This way overlapping days count only once as days off.
        """
        return len(self.adjusted_vacation_days.union(self.adjusted_holiday_days))

    def calculate_actual_working_days(self) -> int:
        """
        To get actual working days as returned by work_calendar.
        Assumes work_calendar handles all filtering.
        """
        return self.work_calendar.calculate_worked_days(self.start_date, self.end_date)

    def calculate_actual_working_hours(self) -> float:
        """
        To return the actual worked hours in the period using the calendar.
        """
        return self.work_calendar.calculate_worked_hours(self.start_date, self.end_date, self.all_day_policy)
    
    def calculate_expected_working_hours(self) -> float:
        """
        To calculate expected working hours based on the user's weekly hours and
        the number of expected working days in the period.
        """
        total_working_days = self.calculate_expected_working_days()
        # Number of weekdays in contract (e.g., Mon–Fri = 5)
        working_days_per_week = len(self.user.contract_working_weekdays)
        # Hours per day = total weekly hours divided by number of working days
        hours_per_day = self.user.weekly_contract_hours / working_days_per_week
        return round(total_working_days * hours_per_day, 2)

    def print_summary(self):
        print("-----------------------------------------------------")
        print(f"Reporting from {self.start_date} to {self.end_date}")
        print("-----------------------------------------------------")
        print(f"Name: {self.user.name}")
        print(f"User contract weekdays: {self.user.contract_working_weekdays}")
        print(f"Vacation days (raw): {sorted(self.vacation_days)}")
        print(f"Holiday days (raw): {sorted(self.holiday_days)}")
        print(f"Overlapping days: {sorted(self.overlapping_days)}")
        print(f"Adjusted vacation days: {sorted(self.adjusted_vacation_days)}")
        print(f"Adjusted holiday days: {sorted(self.adjusted_holiday_days)}")
        print(f"Expected working days: {self.calculate_expected_working_days()}")
        print(f"Vacation days count: {self.calculate_vacation_days_count()}")
        print(f"Holiday days count: {self.calculate_holiday_days_count()}")
        print(f"Total days off: {self.calculate_total_days_off()}")
        print(f"Actual worked days: {self.calculate_actual_working_days()}")
        
        expected_hours = self.calculate_expected_working_hours()
        actual_hours = self.calculate_actual_working_hours()
        difference = round(actual_hours - expected_hours, 2)
        
        if difference > 0:
            diff_label = f"{abs(difference)} hours above expected"
        elif difference < 0:
            diff_label = f"{abs(difference)} hours below expected"
        else:
            diff_label = "exactly on target"
        
        print(f"Expected working hours: {expected_hours}")
        print(f"Actual worked hours: {actual_hours}")
        print(f"Difference: {difference} ({diff_label})")


def report_testing():
    print("-------------------------------------------")
    print("👋 Welcome to the Working Hours Analyser!🔍")
    print("-------------------------------------------")
    user = get_user_data()
    print("\nUser data succesfully collected:")
    print(f"Name: {user.name}")
    print(f"Week Hours: {user.weekly_contract_hours}")
    print(f"Country Code: {user.country_code}")
    start = date(2025, 1, 1)
    end = date(2025, 1, 31)
    all_day_policy = "omit"
    work_calendar = get_calendar_data()
    vacation_calendar = get_vacation_calendar()
    holiday_calendar = get_holiday_calendar(user.country_code)
    report = Report(user, work_calendar, vacation_calendar, holiday_calendar, start, end, all_day_policy)
    report.print_summary()
    print("lets check if calculations were correct with the data given:")
    print(f"user' working: week{user.contract_working_weekdays}")
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


report_testing()

