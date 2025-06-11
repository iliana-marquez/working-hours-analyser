# Working Hours Analyser

#### The Problem: 

> Managing flexible work schedules, part-time contracts, and shifting expectations around hours worked is often confusing and inconsistent, especially when using generic tools like calendars or time trackers. Users frequently lack a clear way to compare their actual working time with what’s expected under their contract or agreement, making it hard to track surplus or deficit hours, plan leave effectively, or advocate for themselves. This creates a real pain point — particularly for freelancers, flexible workers or part-time employees — who need visibility and control over their time without complex setups or guesswork.

#### The Solution:

> Build a tool that connects to your Google Calendar to calculate your actual hours worked versus your contracted hours, while also tracking vacation and local public holidays to generate accurate, detailed reports - all designed to support flexible work schedules and adapt to individual contract or agreement terms.

#### The Result:

> ### [Working Hours Analyser Tool](https://working-hours-analyser-1a0bd1b9ba29.herokuapp.com/) 🔗 <br><br> ![alt text](/assets/doc-images/image.png)

#### The Details:
>- [Overview](#overview)
>- [Purpose](#purpose)
>- [Target Audience](#target-audience)
>- [Features](#features)
>- [User Stories (MVP)](#user-stories-mvp)
>     - [Core Application Setup](#core-application-setup)
>     - [User Input & Configuration](#user-input--configuration)
>     - [Data Processing & Analysis](#data-processing--analysis)
>     - [Reporting & Output](#reporting--output)
>- [UX Features](#ux-features)
>- [Development Process](#development-process)
>     - [Project Planning](#project-planning)
>     - [Project Setup](#project-setup)
>     - [Architecture](#architecture)
>     - [Class Structure](#class-structure)
>     - [Dependencies](#dependencies)
>     - [Python Libraries](#python-libraries)
>     - [Scope](#scope)
>     - [Globals](#globals)
>     - [Connection Test](#connection-test)
>     - [Classes Development](#classes-development)
>     - [Bug Fixes & Validation](#bugs--issues-found-during-development)
>     - [Code Validation](#code-validation)
>- [Testing](#testing)
>     - [Manual Testing Procedure](#manual-testing-procedure)
>     - [Test Calendars](#test-calendars)
>     - [Service Account](#service-account)
>- [Future Enhancements](#future-enhancements)
>- [Acknowledgments](#acknowledgments)
>- [Key Takeaways](#key-takeaways)

---
## Overview
The **Working Hours Analyser** is a command-line tool that automates the tracking of work hours by connecting to your Google Calendar. It transforms scheduled events into precise work hour reports, accounting for public holidays and vacation entries to deliver accurate insights.

## Purpose
Say goodbye to manually tracking shifts in notebooks or clunky spreadsheets! This tool provides:
- Automated analysis of work hours from Google Calendar events.
- Comparison of actual hours worked against contract hours.
- Exclusion of public holidays and vacation days for precise calculations.
- Detailed shift breakdowns and summary reports in the terminal.

## Target Audience
- **Flexible & Part-Time Employees**: Verify hours against contracts for fairness and transparency.
- **Freelancers & Consultants**: Generate accurate time reports for invoicing and pricing.
- **Students**: Monitor time spent on study sessions and academic projects.

## Features
1. **User Interaction**: Handles input/output to gather user information.
2. **Google Calendar Integration**: Fetches and processes calendar events.
3. **Public Holidays**: Uses the `holidays` package to adjust calculations locally.
4. **Contract & Time Calculations**: Computes worked hours, expected hours and differences.
5. **Vacation Tracking**: Excludes vacation events from work hour calculations.
6. **Reporting**: Displays summary and detailed shift reports in the terminal.

## User Stories (MVP)

### Core Application Setup
- As a user, I want to understand what the Working Hours Analyser does and how it benefits me.

### User Input & Configuration
- As a user, I want to:
  - Input my name for personalized reports.
  - Specify my Google Calendar ID for work events.
  - Provide weekly contract hours (e.g., 26.5) and days of my standard working week (e.g. Mo-Fr) for comparison.
  - Enter my country code (e.g., 'AT' for Austria) for local public holiday adjustments.
  - Define a report period (start and end dates in DD.MM.YYYY format).
  - Specify an optional vacation calendar ID and title filter (e.g., "Urlaub Iliana").
  - Receive clear prompts for all inputs.
  - Get validation and helpful error messages for invalid inputs.

### Data Processing & Analysis
- As a user, I want the tool to:
  - Fetch confirmed, timed events from my work calendar within the report period.
  - Exclude public holidays for my country from expected worked hours.
  - Exclude vacation events (matching a title filter) from expected worked hours.
  - Calculate the total duration of actual working events.
  - Compute expected contract hours based on my weekly rate.
  - Compare actual worked hours against expected hours and show the difference.

### Reporting & Output
- As a user, I want:
  - A terminal summary report with my name, report period, expected hours, actual hours and difference.
  - An option to view a detailed list of individual shifts.
  - The ability to generate another report without restarting the application.

## UX Features
- **Clarity**: Concise prompts with examples (e.g. "Mon-Fri").
- **Efficiency**: Single report menu and separate ID / filter prompts.
- **Error Prevention/Recovery**: Specific error feedback (e.g., "Invalid .calendar ID").
- **Consistency**: Uniform tone ("Great!"), separators ("---"), and options ("continue/back/exit").
- **Engagement**: Friendly emojis (😊, 🎉, etc.) and personalized feedback (e.g., "Goodbye, Iliana!").

---
## Development Process

### Project Planning
- Logic was planned by simulating the user flow to identify tasks and actors (user, calendars, report). 
   <details>
   <summary>Click to display terminal output simulation 👇</summary>

   ```
   $ python run.py
   ---------------------------------------------------
   👋 Welcome to Working Hours Analyser 🔍
   ---------------------------------------------------

   📆 Say goodbye to clunky spreadsheets!

   This tool connects with your Google Calendar to track:
   
      • Actual vs. expected hours
      • Workdays, vacation & public holidays
      • Detailed shift breakdowns

   🔧 Setup takes less than 1 minute, just: 
      
      1️⃣  Enter your Info & Calendar ID(s)
      2️⃣  Set your report period and...

   Voilà! Report delivered 🚀

   ---------------------------------------------------
   Let's get your time tracking sorted 👍
   ---------------------------------------------------
   Enter your name: 
   > Iliana

   Please enter your country's two-letter code (e.g., 'AT' for Austria):
   > AT
   
   What are your weekly contract hours (e.g., 26.5)?
   > 26.5
   
   What is your standard working week?
   -------------------------------------------
   1. Mon–Fri
   2. Mon–Sat
   3. Flexible (Every day)
   4. Custom (Other specific days or range)
   -------------------------------------------
   Type the selected option number: 
   > 4

   Enter your working days (mon, tue, wed, thu, fri, sat, sun):
   ------------------------------------------------------------
   You can enter:
   • A range of days (e.g. Mon-Fri or Fri–Mon)
   • A list of specific days (e.g. Mon Tue Fri)
   ------------------------------------------------------------
   > Mo-fri

   Enter the start date for your report (DD.MM.YYYY):
   > 01.05.2024

   Enter the end date for your report (DD.MM.YYYY):
   > 31.05.2024

   If present, how do you wish to handle your all-day working events? 
   -------------------------------------------
   1. Omit
   2. Count them as 8hr shifts
   3. Count them as 24hr shifts 
   -------------------------------------------
   Type the selected option number:
   >

   Now, let's get your Google calendar ID.
   🔍 Do you know where to find it? (yes/no)
   (If yes continue to next question, if not present instructions:)
   —----
   How to Find Your Google Calendar ID
   1. Open Google Calendar in your web browser.
   2. On the left sidebar, under "My calendars" or "Other calendars", find the calendar you want to use.
   3. Click the three dots next to the calendar name, then select "Settings and sharing".
   4. Scroll down to the "Integrate calendar" section.
   5. Find the field labeled "Calendar ID" — it usually looks like an email address (e.g., your.email@gmail.com) or a long string ending with @group.calendar.google.com.
   6. Copy this Calendar ID and paste it into the application when prompted.
   —----

   Please enter the ID of the calendar that holds your WORK events 💼 :
   > 130117b726fac70ced@group.calendar.google.com

   Enter a keyword or event title to filter your work events or press enter to skip.
   >

   (validate, if not a right format print again or make sure the service account is grated access)
   print("""⚠️ WARNING: Your calendar events appear to only show free/busy information.
   This usually means your service account has insufficient permission to see event details.
   Please make sure:
   - The service account email [working-hours-analyser-sa@working-hours-analyser.iam.gserviceaccount.com] 
   is added as a calendar member with at least 'See all event details' permission.
   - If your calendar is in a Google Workspace org, check sharing restrictions.
   """)

   Please enter the ID of the calendar that holds your VACATION events 🏖️ :
   > mitarbeiter_urlaub

   Enter a keyword or event title to filter your vacation events (or press Enter to skip):
   > Urlaub Iliana


   ---------------------------------------------------
   Processing your request... 
   ---------------------------------------------------
   🧠 Analysing data for Iliana from 01.01.2025 to 01.02.2025
   (excluding working-week public holidays and vacation days)...

   ---------------------------------------------------
   Your Working Hours Report: May 2024
   ---------------------------------------------------
   Name: Iliana
   Report Period: 01.05.2024 - 31.05.2024
   Working Week: Mo- Fr / 26.5hrs
   Expected working hours (based on contract): 114.83 hours
   Actual worked hours (from Google Calendar): 102.00 hours
   Difference: 12.83 hours below expected
   ---------------------------------------------------
   Do you want to see your amount of days worked and days of vacations?
   > yes

   >>> Getting your Days Report…

   ---------------------------------------------------
   Your Days Report: May 2024
   ---------------------------------------------------
   Name: Iliana
   Working Week: Mo- Fr / 26.5hrs
   Report Period: 01.05.2024 - 31.05.2024
   Working days: 16
   Vacations days: 3 
   Holiday days: 1
   ---------------------------------------------------
   Vacation days list: [date, title]
   Holiday days list: [date, title]
   ---------------------------------------------------

   Do you want to see a detailed list of your shifts for this period? (yes/no)
   > yes

   >>> Getting your Shifts Report…

   ---------------------------------------------------
   Your Shifts Report: May 2024
   ---------------------------------------------------
   Name: Iliana
   Report Period: 01.05.2024 - 31.05.2024
   Working Week: Mo-Fr / 26.5hrs
   Total Nr. of Shifts: 5
   02.05.2024 09:00 - 17:00: Team Sync (8.0 hrs)
   03.05.2024 09:00 - 16:30: Project X Deep Dive (7.5 hrs)
   06.05.2024 09:00 - 17:00: Client Meeting (8.0 hrs)
   07.05.2024 09:00 - 17:00: Development Work (8.0 hrs)
   08.05.2024 09:00 - 13:00: Code Review (4.0 hrs)
   ---------------------------------------------------

   Do you want to generate another report? (yes (go back to enter report dates) /no)
   > no

   Thank you for using the Working Hours Analyser! Goodbye, Iliana!

   ```

   </details>
<br>

- A [GitHub project board](https://github.com/users/iliana-marquez/projects/10) tracked tasks for project completition:
  - Project Dependencies Setup and Deployment.
  - User input collection (name, contract hours, calendar IDs).
  - Data processing (fetch events, exclude holidays/vacations).
  - Report generation (summary, shifts, days).

### Project Setup
- Created a repository using the Code Institute P3 template.
- Connected to a Heroku project for early deployment and testing.
- Enabled Google APIs (Worksheet, Drive, Calendar) in Google Cloud.
- Added service account email as editor to the worksheet.
- Generated `creds.json` and added it to `.gitignore`.
- Installed dependencies: `gspread`, `google-api-python-client`, `holidays`.
- Reinstalled requirements via `pip freeze > requirements.txt`.

### Architecture
- **OOP Structure**:
  - **Encapsulation**: Each class manages its own data and behavior.
  - **Abstraction**: Hides calendar fetching details from the rest of the app.
  - **Single Responsibility**: Each class has one clear purpose.
  - **Inheritance**: Allows easy addition of new calendars/features without massive refactoring.

- **Defining the classes**
   - **User Class**:
      - To encapsulate user related data (name, contract hours, country code).
      - Easier to pass around a single user object instead of multiple parameter.
      - To keep user-related logic centralized.
      - Readable and scalable for future adding of more attributes.
   - **Calendar Classes**:
      - To encapsulate calender related data (calendar_id).
      - Easier to abstract calendar access and operations (fetching events, filtering, etc.).
      - Perform calculations to return the Calendar Events (days, hours, etc...).
   - **Report Class**:
      - Handles user and calendar data to perform calculations and generate the report output.

### Class Structure and Data Types
🧑‍💼 **User**
- name: str
- weekly_contract_hours: float
- contract_working_weekdays: list[days in a working week] (updated)
- country_code: str

📅 **Calendar** (base class)
- calendar_id: str
- fetch_events_by_period(start_date: date, end_date: date) -> list[Events]
- filter_events_by_title(str) -> list[Event]
 
💼 **WorkCalendar** (inherits from Calendar)
- title_filter: Optional[str]
- fetch_filtered_events(start_date: date, end_date: date) -> list[Event]
- get_shifts() -> list[Event]
- calculate_worked_hours(start_date, end_date) -> float
- calculate_worked_days(start_date, end_date) -> int

🌴 **VacationCalendar** (inherits from Calendar)
- title_filter: Optional[str]
- get_vacation_days(start_date: date, end_date: date) -> set
- calculate_vacation_days(start_date, end_date) -> int

🌎 **HolidayCalendar** (not a calendar, wraps the holidays package)
- country_code: str
- fetch_holidays(start_date, end_date, country_code) -> List[Dict[str, any]]
- count_holidays(start_date, end_date) -> int

📊 **Report** (manager Class)
- user (User instance)
- work_calendar (WorkCalendar instance)
- vacation_calendar (optional VacationCalendar instance)
- holiday_calendar (HolidayCalendar instance)
- start_date: date
- end_date: date
- all_day_policy: str
- calculate_expected_working_days() -> int
- calculate_vacation_days_count() -> int
- calculate_holiday_days_count() -> int
- calculate_total_days_off() -> int
- calculate_actual_working_days_off() -> int
- calculate_actual_working_hours() -> float
- calculate_expected_working_hours() -> float
- print_summary() -> 
   - print_hours_report()
   - print_days_report()
   - print_shifts_report()

### Main()
   Collects period and all-day policy from user input to pass it to Report class to create a report instance.
   - all_day_policy: ('omit', '8hr', '24hr')
   - start_date: date
   - end_date: date
   - Report.print_summary()

### Dependencies
- **gspread**: Essential for connecting to and updating Google Sheets for report storage.
- **google.oauth2.service_account.Credentials**: Required for secure authentication with Google APIs via service account.
- **google hammapiclient.discovery.build**: Necessary to build a client for Google Calendar API to fetch events.
- **holidays**: Critical for fetching country-specific public holidays to exclude from work hour calculations.

### Python Libraries
- **datetime**: Provides tools for manipulating dates and times, such as creating, formatting, and comparing them.
- **dateutil**: Enhances datetime with flexible date parsing, relative time shifts, and timezone handling.
- **typing**: Enables type hints to clarify function inputs and outputs, improving code readability and safety.
- **re**: Enables pattern matching and text searching using regular expressions.

### Scope
````
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar.readonly"
]
````

### Globals
- `CREDS`: Loaded from `creds.json` via service account.
- `SCOPE_CREDS`: Credentials with defined scopes.
- `GSPREAD_CLIENT`: Authorized gspread client.
- `SHEET`: Opened 'working-hours-reports' sheet.
- `CALENDAR_SERVICE`: Built for Calendar API v3.
- `WEEKDAYS_ORDERED`: Ordered list of weekdays for calculation logic.
- `WEEKDAY_ALIASES`: Maps broader variations of weekday inputs to standard weekday names (e.g., for flexible input matching).
- `_has_shown_calendar_id_help`: Flag to indicate whether calendar ID help has already been shown.

### Connection Test
- Tested dependencies locally and on deployed Heroku app and moved testing code to test.py
- Validated calendar connection (e.g., "Iliana AM/GM Home office")
- Confirmed Google Worksheet connection
> ![alt text](/assets/doc-images/dependencies-connection-test.png)

### Classes Development 
   > **⚠️ Important Note on `cls` Convention**: <br> Instead of the conventional `cls`, class methods use descriptive names like `user_class` or `calendar_class` to clearly indicate the class being instantiated. This choice was made intentionally to aid learning, improve readability and ease debugging - especially for those new to OOP concepts.

- Develop **User Class**, test locally and on deployed heroku app
      ![alt text](/assets/doc-images/user-class-test.png)
- Develop **Calendar Class**, test locally and on deployed heroku app
      ![alt text](/assets/doc-images/calendar-class-test.png)
- Develop **Calendar Class**, test locally and on deployed heroku app
      ![alt text](/assets/doc-images/calendar-class-test.png)
- Develop **WorkCalendar Subclass**, test locally and on deployed heroku app
      ![alt text](/assets/doc-images/workcalendar-class-test.png)
- Develop **VacationCalendar Subclass**, test locally and on deployed heroku app
      ![alt text](/assets/doc-images/vationcalendar-class-test.png)
- Develop **HolidayCalendar**, test locally and on deployed heroku app
      ![alt text](/assets/doc-images/holidaycalendar-class-test.png)
- Develop **Report Class**, test locally and on deployed heroku app
      ![alt text](/assets/doc-images/summary-report-test.png)

### Bugs & Issues Found During Development
- **Incorrect Keyword Filtering**
   - **Bug:** The `WorkCalendar` & `VacationCalendar` failed to filter events by keyword properly in the `fetch_filtered_events(self, start_date, end_date)` method, as it was returning all events within range instead of the filtered ones
   - **Cause:** Used `filter_events_by_period()` instead of a title-based filter.
   - **Fix:** Replaced with `filter_events_by_title()` from the base Calendar class.
      ````
      return self.filter_events_by_title(self.title_filter)
      ````
   
- **Broken Shift Filtering**
   - **Bug**: on the `get_shifts()` method all events were fetched, not only the filtered ones fetch_events_by_period. 
   - **Cause**:  Misuse of `filter_events_by_period()`.
   - **Fix**: Instead of the given `filter_events_by_period()`, used the accurate `fetch_filtered_events()` for the `get_shifts()` method for accurate calculations if a filter keyword is given.
      ````
      events = self.fetch_filtered_events(start_date, end_date) 
      ````
- **Vacation Events Spanning Outside the Date Range**
   - **Issue**: Vacation events spanning beyond the given time range were counted in full, including days outside the specified period.
   - **Fix**: Clip the start and date of the given period to the user-specified date range to count only the days within this range.
      ```
      clipped_start = max(date_start, start_date)
      clipped_end = min(date_end, end_date)
         if clipped_start <= clipped_end:
         for single_day in range((clipped_end - clipped_start).days + 1):
            day = clipped_start + timedelta(days=single_day)
            vacation_days.add(day)
      ```

- **Overflowing Workshifts**      
   - **Issue**: Shifts that began before the start_date but extended into the range were not being counted.
   - **Fix**: Adjusted event fetching to include shifts starting one day before the start_date, ensuring that any overflow into the selected range is captured.
   ````
   expanded_start = start_date - timedelta(days=1)
   ````

   
   - **Issue**: Shifs that started before or ended were overcounted.
   - **Fix**: Implemented shift "clipping" logic to only count the portion of a shift that falls within the user-given range.
   ```
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
   ```

- **Google Calendar Pagination Limit**
   - **Bug**: Long date ranges returned incomplete data, leading to inaccurate work hour totals (e.g., negative surplus).
   - **Cause**: The tool retrieved only the first 250 events due to Google Calendar API limits.
   - **Fix**: Implemented pagination by checking for nextPageToken and looping through all pages until completion.
   ````
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
   ````

- **Report Class logic implementation to accurate calculate expeted vs. actually worked time**
   - **Issue**: A date that is both a public holiday and part of a vacation period should never be counted twice, nor should a public holiday be treated as personal vacation.
   - **Solution**: Identify the overlap, subtract it from the vacation set, and leave it out of the holiday set.
   ````
        # Get sets of vacation and holiday days
        self.vacation_days: Set[date] = self.vacation_calendar.get_vacation_days(start_date, end_date)
        self.holiday_days: Set[date] = {h['date'] for h in self.holiday_calendar.holidays}
        # Calculate overlapping holiday days within vacation days
        self.overlapping_days: Set[date] = self.vacation_days & self.holiday_days
        # Adjust vacation days by removing overlapping holidays
        self.adjusted_vacation_days: Set[date] = self.vacation_days - self.overlapping_days
   ````

   - **Issue**: How not to count holidays falling on non-working days (e.g., weekends) or on vacation.
   - **Solution**: Only count holidays that are working days and not overlapping with vacation.
   ````
   contract_workdays = self.user.get_contract_working_weekdays_dates(start_date, end_date)
   self.adjusted_holiday_days: Set[date] = {
      day for day in self.holiday_days
      if day in contract_workdays and day not in self.vacation_days
   }
   ````

- **Calendar ID Validation & CLI Feedback Implementation**
   - **Issue**: Users may input an invalid Calendar ID.
   - **Cause**: Users may don't know where to find their Calendar ID.
   - **Fix**: Prompt user for Calendar ID with clear examples (e.g., name@gmail.com or xyz@group.calendar.google.com) and check for valid format before processing.
   ---
   - **Issue**: Users may input a valid but inaccessible Calendar ID.
   - **Cause**: Service account is not added to the calendar.
   - **Fix**: Add instructions on how to add the service to the calendar and grant access to it.
   ---
   - **Issue**: Users my have added the servie to the calendar, but not granted the needed access of at least read only show all details
   - **Cause**: Some corporate calendars may restrict access to external accounts or user might not know hot to grant the needed access.
   - **Fix**: Inform user if permissions are missing, show the exact steps to grant the needed access to the service account and highlight potential Google Workspace admin restrictions.

- **Last Minute Bugs**
   - **Bug**: Invalid Country Code Crash
   - **Fix**: Wrapped main() and holiday lookup in a try/except block to catch errors and restart the process gracefully.
   ---
   - **Bug**: When no events were found, the app still attempted to generate a report.
   - **Fix**: Added a conditional check — if no events are found, the report is skipped and the user is notified.
   ---
   - **Bug**: Vacation days were being counted even when they fell outside the contractual working week.
   - **Fix**: Updated the logic to exclude non-contractual days from `adjusted_vacation_days`, so only vacation days that fall within the working week are counted.
   ---
   - **Issue**: Looping through the reporting, by keeping User data and making a new report or restarting the application was not UX oriented.
   - **Fix**: Split Main() function into separete methods to gather and process the data so it can be looped to specific steps throughout the CLI flow.


### Code Validation
- **Manual Testing**: Tested locally and on Heroku with sample calendars, verifying hours (101.00), days (18), and vacation (3) for 01.01.2025 - 31.01.2025
- **PEP Validation**: Used [CI Python Linter](https://pep8ci.herokuapp.com/) and `flake8` to ensure PEP 8 compliance
  - **1st Result** after first validation: 118 Errors.
      - Fixed line length
      - Removed whitespaces and blank lines
  - **2nd Result** after corrections: All clear, no errors found.

---
## Testing

### Manual Testing Procedure
- **Setup**: Used test calendars (Iliana, Cesar, Angela) and service account for access
- **Test Cases**:
  - Entered valid/invalid calendar IDs to check validation
  - Tested date ranges especific ranges for event fetching
  - Verified holiday/vacation exclusion with sample data
  - Tested Calendar with no details access, no report possible. 
- **Outcome**: Confirmed accuracy of report restults with data of shifts by verifying report result data with period range and shifts sum

### Test Calendars
- **Iliana**: `vcrk5gevoffaskk157rbl3q1n8@group.calendar.google.com`
- **Cesar** (starts 01.03.2025): `66bf19679262cea6dda330aa828b21fcd59399f1fe0969130117b726fac70ced@group.calendar.google.com`
- **Angela** (ends 28.02.25): `s2msasa4r6ppgpauhjt9h0enu8@group.calendar.google.com`
- **Urlaube-Mitarbeiter** (keywords: `urlaub cesar`, `urlaub iliana`, `urlaub angela`): `11knrbjev3res0paa1gkcug9js@group.calendar.google.com`

### Service Account
- If you want to get reports on your own calenders:
   - Grant at least read-only / show all details access to: `working-hours-analyser-sa@working-hours-analyser.iam.gserviceaccount.com`
   - **Note***: Hidden details in calendars won’t be handled and return no events

---
## Future Enhancements
- **Custom All-Day Policy**: Allow users to input a custom hour value for all-day events.
- **Sick Days**: Handle sick days based on country rules and doctor’s notes.
- **Time Bonuses**: Calculate bonuses for after-hours, weekends, or holidays (e.g., in Austria, post-18:30 hours = 1.5x).
- **Input Validation**: Instant feedback for incorrect user inputs (e.g., typo in name, incorrect workig week hours number, etc.).
- **Calender Validation**: Add an elegant flow to loop to the start or exit if desired by the user, at the moment, the only options are try again (to entry the ID) or type cancel to exit (Operation cancelled).
- **User Confirmation**: Display entered data (calendar IDs, filters) for confirmation before printing report.
- **Written Reports**: Export reports via gspread or JSON for API use.
- **Broader Calendar Support**: Integrate CalDAV for non-Google calendars.
- **User Stories (Post-MVP)**
   -  **User Authentication**
      - As a first-time user, I want:
      - Guidance through Google Calendar authentication
      - To fetch my own calendars after authentication
      - Secure, ephemeral storage of my access token for the session
      - Clear error messages if authentication fails
   - **Reporting & Output**
      - As a user, I want a written report (worksheet) for personal use, invoicing, or sharing with bosses/clients

---
## Acknowledgments
- [Code Institute](https://codeinstitute.net/global/): For the [P3 Project Template on GitHub](https://github.com/Code-Institute-Org/p3-template) and the ["Love Sandwiches" Project](https://github.com/Code-Institute-Solutions/love-sandwiches-p5-sourcecode) walkthrough, which inspired this automated Google API interaction.
- All external code from libraries (`gspread`, `google-api-python-client`, `holidays`) sourced from PyPI.
- [Markdown Cheatsheet – Markdown Here](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet): Helpful for quick reference to Markdown syntax used throughout this README.
- [GitHub Docs – Organizing Information with Collapsed Sections](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/quickstart-for-writing-on-github): Used to create collapsible sections for things like the terminal simulation on this README.

---
## Key Takeaways
- **Plan First**: Simulate desired outcomes to identify tasks and actors.
- **OOP Power**: Use encapsulation, abstraction, inheritance, and polymorphism for modular, scalable code.
- **User Focus**: Solve familiar problems, then scale to collective needs.
- **Simplicity**: Keep it simple for easier development and debugging.
- **Critical Thinking**: Identifying objects and responsibilities transcends tech stack, enabling faster learning of new languages or tools.
