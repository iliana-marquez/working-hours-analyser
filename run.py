import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import holidays
from datetime import datetime, date, timedelta

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
    return User.from_input()


def main():
    print("------------------------------------------")
    print("👋  Welcome to the Working Hours Analyser!")
    print("------------------------------------------")
    user = get_user_data()
    print("\nUser data succesfully collected:")
    print(f"Name: {user.name}")
    print(f"Name: {user.weekly_contract_hours}")
    print(f"Name: {user.country_code}")


main()


