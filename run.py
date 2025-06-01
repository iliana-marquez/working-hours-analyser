import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import holidays
# from datetime import datetime, date, timedelta

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


def fetch_calendar():
    """
    test function to check API connection and fetch calendar info
    """
    calendar_id = input("Please enter your calendar ID:\n")
    try:
        calendar_info = CALENDAR_SERVICE.calendars().get(calendarId=calendar_id).execute()
        print("Calendar connected successfully!")
        print("Calendar name: ", calendar_info['summary'])
    except Exception as e:
        print("Error fetching calendar:", e)


def fetch_worksheet():
    """
    test function to check API connection and fetch worksheet info
    """
    worksheet_name = input("please enter the name of your worksheet")
    try:
        reports = SHEET.worksheet(worksheet_name).get_all_values()
        headings = reports
        print(headings)
    except Exception as e:
        print("Error fetching worksheet:", e)


def fetch_holidays(year):
    """
    test function to check Holyday dependency and fetch holidays info
    """
    country = input("Please type your country code:\n")
    holiday_list = holidays.country_holidays(country, years=year)
    for date, name in holiday_list.items():
        print(f"{date}: {name}")


print("Testing google calendar connection:")
fetch_calendar()
print("Testing google worksheet connection:")
fetch_worksheet()
print("testing holiday library connection:")
fetch_holidays(2025)
print("we are good to go")
