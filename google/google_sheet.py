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

from datetime import datetime

def append_mac_address(mac_address: str):
    try:
        sheet = init_google_sheet()
        all_records = sheet.get_all_records()  # Список словарей

        # Найти индекс строки с этим MAC (если есть)
        existing_row_index = None
        for i, row in enumerate(all_records):
            if row.get("MAC") == mac_address:
                existing_row_index = i + 2  # +2 потому что get_all_records пропускает заголовки и индексация с 1

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if existing_row_index:
            # Обновляем существующую строку
            sheet.update(f"B{existing_row_index}", now)
            print(f"🔁 Обновлён MAC: {mac_address}")
        else:
            # Добавляем новую строку
            sheet.append_row([now, mac_address])
            print(f"✅ Добавлен MAC: {mac_address}")

    except Exception as e:
        print(f"❌ Ошибка при добавлении MAC: {e}")
