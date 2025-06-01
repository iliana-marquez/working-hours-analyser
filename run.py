import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
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
    try:
        reports = SHEET.worksheet('reports').get_all_values()
        headings = reports 
        print(headings)
    except Exception as e:
        print("Error fetching worksheet:", e)


fetch_worksheet()