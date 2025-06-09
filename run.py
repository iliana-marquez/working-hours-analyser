import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import holidays
from datetime import datetime, date, timedelta, time, timezone
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

_has_shown_calendar_id_help = False


class User:
    def __init__(
        self, name: str,
        country_code: str,
        weekly_contract_hours: float,
        contract_working_weekdays: List[str]
    ):
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
            country_code = input(
                "\nPlease enter your country's two-letter code (e.g., 'AT' for Austria):\n> "
            ).strip()
            if len(country_code) == 2 and country_code.isalpha():
                break
            print(
                "Your country code must be exactly two letters, please try again."
            )
        while True:
            hours_input = input(
                "\nWhat are your weekly contract hours (e.g., 26.5)?\n> "
            ).strip()
            try:
                weekly_contract_hours = float(hours_input)
                break
            except ValueError:
                print(
                    "Please enter a valid number (e.g., 26.5) for calculations."
                )

        contract_working_weekdays = user_class.get_contract_working_weekdays()

        return user_class(
            name,
            country_code,
            weekly_contract_hours,
            contract_working_weekdays
        )
    
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


def get_and_validate_calendar_id(
        prompt_text: str = None,
        show_help_if_first_time: bool = True
        ) -> str:
    """
    Helper to get calendar ID from user input with:
      - optional first-time instructions
      - format validation (email-like or 'primary')
      - Google Calendar access validation (read permission)
      - option to exit/cancel input

    Args to show instructions only the first time:
        prompt_text: str = None,
        show_help_if_first_time: bool = True

    Returns:
        str or None: Validated calendar ID, or None if user exits.
    """
    global _has_shown_calendar_id_help
    calendar_id_pattern = r"^[^@]+@[^@]+\.[^@]+$"
    if show_help_if_first_time and not _has_shown_calendar_id_help:
        print("\nNow, let's get your Google calendar ID.")
        print("🔍 Do you know where to find it? (yes/no)")
        response = input("> ").strip().lower()
        if response not in ("yes", "y"):
            print("""
👉 How to Find Your Google Calendar ID:
1. Open Google Calendar in your browser.
2. On the left sidebar, under 'My calendars' or 'Other calendars', find your calendar.
3. Click the three dots next to it, select 'Settings and sharing'.
4. Who has acces, this service must have at least read all details acces: \n working-hours-analyser-sa@working-hours-analyser.iam.gserviceaccount.com as a reader.
4. Scroll to 'Integrate calendar' section.
5. Copy the 'Calendar ID'\n(looks like an email or ends with @group.calendar.google.com).
            """)
        _has_shown_calendar_id_help = True  # Mark as shown
    if prompt_text:
        print(prompt_text)

    while True:
        calendar_id = input("> ").strip()
        if calendar_id.lower() in {"exit", "cancel"}:
            print("Operation cancelled.")
            exit()
        if not (re.match(calendar_id_pattern, calendar_id) or calendar_id.lower() == "primary"):
            print("😳 Invalid format. Please enter a valid Calendar ID (not a full URL or @gmail address).\n")
            continue
        # Check access by trying to fetch one event with details within next 7 days
        now = datetime.now(timezone.utc)
        time_min = now.isoformat()
        time_max = (now + timedelta(days=30)).isoformat()
        try:
            CALENDAR_SERVICE.calendars().get(calendarId=calendar_id).execute()
            events_result = CALENDAR_SERVICE.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=1,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            if events:
                event = events[0]
                # Check if event has a 'summary' or other detail fields visible
                if 'summary' in event and event['summary']:
                    return calendar_id
                else:
                    print("🙈 Your calendar access is limited to free/busy info only, no event details.\n"
                          "Please ensure the service account has 'See all event details' permission.")
            else:
                # No events found but access OK (empty calendar)
                return calendar_id

        except Exception as e:
            print(f"🤔 Could not access this calendar.\n")
            if "notFound" in str(e) or "403" in str(e):
                print("""👉  Please make sure:
- The calendar ID exists.
- You've shared this calendar with the service account:
  working-hours-analyser-sa@working-hours-analyser.iam.gserviceaccount.com
- If it's an organization calendar, ensure it has at least 'See all event details' permission.
""")
            print("Try again or type 'exit' to cancel.\n")


class Calendar:
    def __init__(self, calendar_id: str, title_filter: Optional[str] = None):
        self.calendar_id = calendar_id
        self.events: List[dict] = []
        self.title_filter = title_filter

    @classmethod
    def from_input(calendar_class, is_first_time=False, prompt_text=None):
        """
        Collects and validates the calendar ID from input
        """
        while True:
            calendar_id = get_and_validate_calendar_id(is_first_time, prompt_text)
            if calendar_id is None:
                raise KeyboardInterrupt("Calendar ID input cancelled by user.")                
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
            all_events = []
            page_token = None
            while True:
                events_result = CALENDAR_SERVICE.events().list(
                    calendarId=self.calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy='startTime',
                    pageToken=page_token
                ).execute()
                events = events_result.get('items', [])
                all_events.extend(events)
                page_token = events_result.get('nextPageToken')
                if not page_token:
                    break

            self.events = all_events
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
        calendar_id = get_and_validate_calendar_id(
            prompt_text="\nPlease enter the ID of the calendar that holds your WORK events 💼 :", 
            show_help_if_first_time=True
        )
        title_filter = input("\nEnter a keyword or event title to filter your work events or press enter to skip:\n> ").strip() or None
        return workcal_class(calendar_id, title_filter)

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
        To create an instance of VacationCalendar 
        """
        calendar_id = get_and_validate_calendar_id(
            prompt_text="\nPlease enter the ID of the calendar that holds your VACATION events 🏖️ :",
            show_help_if_first_time=False
        )
        title_filter = input("\nEnter a keyword or event title to filter your vacation events (or press Enter to skip):\n> ").strip() or None
        return vacationcal_class(calendar_id, title_filter)


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
        self.shifts = self.work_calendar.get_shifts(start_date, end_date, all_day_policy)
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
        """
        to print the hour_report by default
        and ask user if a days or shifts report is also wanted
        """
        self.print_hours_report()
        show_days_report = input("\nDo you want to see your amount of worked & vacation days? (yes/no)\n> ").strip().lower()
        if show_days_report in ("yes", "y"):
            self.print_days_report()
        show_shifts_report = input("\nDo you want to see a detailed list of your shifts for this period? (yes/no)\n> ").strip().lower()
        if show_shifts_report in ("yes", "y"):
            self.print_shifts_report()
    
    def print_hours_report(self):
        print("\n---------------------------------------------------")
        print(f"Your Working Hours Report: {self.start_date.strftime('%B %Y')}")
        print("---------------------------------------------------")
        print(f"👤 Name: {self.user.name}\n")
        print(f"📊 Report Period: {self.start_date.strftime('%d.%m.%Y')} - {self.end_date.strftime('%d.%m.%Y')}\n")
        
        expected_hours = round(self.calculate_expected_working_hours(), 2)
        actual_hours = round(self.calculate_actual_working_hours(), 2)
        difference = round(actual_hours - expected_hours, 2)

        if difference > 0:
            diff_label = f"{abs(difference)} ⬆️ hours above expected"
        elif difference < 0:
            diff_label = f"{abs(difference)} ⬇️ hours below expected"
        else:
            diff_label = "🎯 exactly on target"

        print(f"⏱️ Expected working hours (based on contract): {expected_hours} hours\n")
        print(f"✅ Actual worked hours (from Google Calendar): {actual_hours} hours\n")
        print(f"🔁 Difference: {diff_label}")
        print("---------------------------------------------------")
    
    def print_days_report(self):
        print("\n>>> Getting your Days Report…\n")
        print("---------------------------------------------------")
        print(f"Your Days Report: {self.start_date.strftime('%B %Y')}")
        print("---------------------------------------------------")
        print(f"👤 Name: {self.user.name}\n")
        print(f"📊 Report Period: {self.start_date.strftime('%d.%m.%Y')} - {self.end_date.strftime('%d.%m.%Y')}\n")
        print(f"📅 Expected working days: {self.calculate_expected_working_days()}\n")
        print(f"✅ Working days: {self.calculate_actual_working_days()}\n")
        print(f"🏖️ Vacation days: {self.calculate_vacation_days_count()}")
        print("---------------------------------------------------")

    def print_shifts_report(self):
        print("\n>>> Getting your Shifts Report…\n")
        print("---------------------------------------------------")
        print(f"Your Shifts Report: {self.start_date.strftime('%B %Y')}")
        print("---------------------------------------------------")
        print(f"👤 Name: {self.user.name}\n")
        print(f"📊 Report Period: {self.start_date.strftime('%d.%m.%Y')} - {self.end_date.strftime('%d.%m.%Y')}\n")

        for shift in self.shifts:
            date_str = shift["start"].strftime("%d.%m.%Y")
            time_range = f" {shift['start'].strftime('%H:%M')} - {shift['end'].strftime('%H:%M')}"
            duration = round(shift["duration"], 1)
            print(f"👉 {date_str} {time_range}: {shift['title']} ({duration} hrs)")
        print("---------------------------------------------------")


"""
Helper and flow methods
"""
def print_banner():
    print("---------------------------------------------------")
    print("👋 Welcome to Working Hours Analyser 🔍")
    print("---------------------------------------------------")
    print("📆 No more spreadsheets — track time effortlessly!\n")
    print("⏱️  This tool connects to your Google Calendar and automatically")
    print("calculates actual vs. expected hours, time balance,")
    print("vacations, holidays and gives you a clean shift summary.\n")
    print("🔧 All you'll need:")
    print("Calendar ID(s), contract hours & a date range.\n")
    print("Don't worry - the setup is fully guided and takes less than a minute.")
    print("---------------------------------------------------")
    print("Let's get your time tracking sorted 👍")
    print("---------------------------------------------------")


def main():
    while True:
        try:
            print_banner()
            user = get_user_data()

            def input_date(prompt):
                """
                to get the start_date and end_date for the report range
                """
                while True:
                    user_input = input(prompt).strip()
                    try:
                        return datetime.strptime(user_input, "%d.%m.%Y").date()
                    except ValueError:
                        print("😅 Invalid format. Please use DD.MM.YYYY (e.g. 01.05.2024)")
                
            while True:
                start = input_date("\nEnter the start date for your report (DD.MM.YYYY):\n> ")
                end = input_date("\nEnter the end date for your report (DD.MM.YYYY):\n> ")
                if start > end:
                    print("⚠️ Start date cannot be after end date. Please try again.\n")
                else:
                    break

            print("""\nIf present, how do you wish to handle your all-day working events? 
        1. Omit
        2. Count them as 8hr shifts
        3. Count them as 24hr shifts""")
            all_day_options = {
                "1": "omit",
                "2": "8h",
                "3": "24h"
            }
            while True:
                choice = input("Type the selected option number:\n> ").strip()
                if choice in all_day_options:
                    all_day_policy = all_day_options[choice]
                    break
                else:
                    print("🥴 Invalid option. Please enter 1, 2, or 3.")

            work_calendar = get_calendar_data()
            vacation_calendar = get_vacation_calendar()
            holiday_calendar = get_holiday_calendar(user.country_code)
            print("\nProcessing your request... ⌛ This may take a moment as we fetch events.")
            print(f"🧠 Analyzing data for {user.name.capitalize()} from {start.strftime('%d.%m.%Y')} to {end.strftime('%d.%m.%Y')} (excluding public holidays and vacation events)...")
            report = Report(user, work_calendar, vacation_calendar, holiday_calendar, start, end, all_day_policy)
            
            if report.calculate_actual_working_hours() == 0 or report.calculate_actual_working_days() == 0:
                print("\n No working events found in the selected calendars during this period.")
                retry = input("Would you like to try a different date range? (yes/no)\n> ").strip().lower()
                if retry in ("yes", "y"):
                    print("🔁 Restarting to allow new date range selection...\n")
                    continue  # Go back to the start of the loop
                else:
                    print("\n👋 Thank you for using the Working Hours Analyser. Goodbye!")
                    return
            else:
                report.print_summary()


            def run_report_loop(user, work_calendar, vacation_calendar, holiday_calendar, all_day_policy):
                while True:
                    print("\nEnter the period range for your NEW report:")
                    start_date = input_date("Start date (DD.MM.YYYY):\n> ")
                    end_date = input_date("End date (DD.MM.YYYY):\n> ")

                    new_report = Report(
                        user=user,
                        work_calendar=work_calendar,
                        vacation_calendar=vacation_calendar,
                        holiday_calendar=holiday_calendar,
                        start_date=start_date,
                        end_date=end_date,
                        all_day_policy=all_day_policy
                    )
                    
                    if new_report.calculate_actual_working_hours() == 0 or new_report.calculate_actual_working_days() == 0:
                        print("\n⚠️ No working events found in the selected calendars during this period.")
                        retry = input("Would you like to try a different date range? (yes/no)\n> ").strip().lower()
                        if retry in ("yes", "y"):
                            print("🔁 Restarting to allow new date range selection...\n")
                            continue 
                        else:
                            print("\n👋 Thank you for using the Working Hours Analyser. Goodbye!")
                            return 
                    else:
                        new_report.print_summary()

                    again = input("\nDo you want to generate another report with the SAME CALENDAR(s)? (yes/no): ").strip().lower()
                    if again not in ("yes", "y"):
                        print("Exiting report generator loop.")
                        break

            while True:
                print("\nDo you want to:")
                print("1. Generate another report with the SAME CALENDARS")
                print("2. Start fresh with NEW CALENDAR(s) *")
                print("3. Exit")
                choice = input("> ").strip()

                if choice == "1":
                    run_report_loop(user, work_calendar, vacation_calendar, holiday_calendar, all_day_policy)

                elif choice == "2":
                    print("\n🔁 Restarting setup...\n")
                    main()  
                    break

                elif choice == "3":
                    print("\n👋 Thanks for using Working Hours Analyser. Goodbye!")
                    break

                else:
                    print("Please enter 1, 2 or 3.")
        except Exception as e:
            # NEW: Global error handler
            print(f"\n😅 Oops, something went wrong: {str(e)}")
            retry = input("Would you like to start again? (yes/no)\n> ").strip().lower()
            if retry not in ("yes", "y"):
                print("\n👋 Thank you for using the Working Hours Analyser, have a nice day!")
                break
            print("\n🔁 Restarting...\n")


main()

