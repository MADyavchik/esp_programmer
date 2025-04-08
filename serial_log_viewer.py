# serial_log_viewer.py
import subprocess
import re
import time
from oled_ui import draw_log_table, clear
from buttons import btn_back

LOG_PATTERN = re.compile(r"(Battery|Temp|TOF|Weight):\s*(-?\d+)")

def show_serial_data():
    clear()
    values = {"Battery": "—", "Temp": "—", "TOF": "—", "Weight": "—"}

    # Запускаем subprocess с pio monitor
    proc = subprocess.Popen(
        ["platformio", "device", "monitor", "--baud", "115200", "--port", "/dev/cu.usbserial-0001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    try:
        for line in proc.stdout:
            match = LOG_PATTERN.search(line)
            if match:
                key, val = match.groups()
                values[key] = val
                draw_log_table(values)

            # Проверка выхода по кнопке назад
            if btn_back.is_pressed:
                break

    except Exception as e:
        print(f"Ошибка чтения монитора: {e}")

    proc.terminate()
    time.sleep(0.5)
    clear()
