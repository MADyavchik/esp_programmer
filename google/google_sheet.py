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

from datetime import datetime

def append_mac_address(mac_address: str):
    try:
        sheet = init_google_sheet()
        all_records = sheet.get_all_records()

        #print("📋 Все записи:")
        #for row in all_records:
            #print(row)

        # Найти индекс строки с этим MAC (если есть)
        existing_row_index = None
        for i, row in enumerate(all_records):
            if row.get("MAC") == mac_address:
                existing_row_index = i + 2  # +2 из-за заголовка

        now_data = datetime.now().strftime('%d/%m/%Y')
        now_time = datetime.now().strftime('%H:%M:%S')

        row_values = [now_data, now_time, mac_address]

        if existing_row_index:
            # Обновляем существующую строку (все три колонки)
            sheet.update(f"A{existing_row_index}:C{existing_row_index}", [row_values])
            print(f"🔁 Обновлён MAC: {mac_address}")
        else:
            # Добавляем новую строку
            sheet.append_row(row_values)
            print(f"✅ Добавлен MAC: {mac_address}")

    except Exception as e:
        print(f"❌ Ошибка при добавлении MAC: {e}")
