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