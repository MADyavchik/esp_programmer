import subprocess
import re
import time
from threading import Thread, Event
from oled_ui import draw_log_table, clear
from buttons import btn_back
import asyncio

LOG_PATTERN = re.compile(r"(Battery|Temp|TOF|Weight):\s*(-?\d+)")

def monitor_serial_data(proc, stop_event):
    """Функция для мониторинга данных в отдельном потоке"""
    try:
        values = {"Battery": "—", "Temp": "—", "TOF": "—", "Weight": "—"}
        for line in proc.stdout:
            if stop_event.is_set():
                break
            match = LOG_PATTERN.search(line)
            if match:
                key, val = match.groups()
                values[key] = val
                draw_log_table(values)
    except Exception as e:
        print(f"Ошибка чтения монитора: {e}")

    proc.terminate()
    clear()

async def show_serial_data():
    clear()

    stop_event = Event()

    proc = subprocess.Popen(
        ["platformio", "device", "monitor", "--baud", "115200", "--port", "/dev/ttyS0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    monitor_thread = Thread(target=monitor_serial_data, args=(proc, stop_event))
    monitor_thread.start()

    while not btn_back.is_pressed:
        await asyncio.sleep(0.1)  # ← заменили на async-версию

    stop_event.set()
    proc.terminate()
    monitor_thread.join()

    clear()

    return "main"


