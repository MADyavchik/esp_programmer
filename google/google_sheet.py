import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

key_path = os.path.expanduser('~/parsfor-efc9e0058e29.json')

def init_google_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)

    client = gspread.authorize(creds)

    sheet = client.open("ESP_MACs").sheet1

    return sheet

def append_mac_address(mac_address: str):
    try:
        sheet = init_google_sheet()

        # Пример строки: [MAC, Дата и время]
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sheet.append_row([mac_address, now])

        print(f"✅ Добавлен MAC: {mac_address}")
    except Exception as e:
        print(f"❌ Ошибка при добавлении MAC: {e}")
