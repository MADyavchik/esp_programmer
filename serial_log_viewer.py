import asyncio
import subprocess
import re
from oled_ui import draw_log_table, clear
from buttons import btn_back

LOG_PATTERN = re.compile(r"(Battery|Temp|TOF|Weight):\s*(-?\d+)")

async def monitor_serial_data(proc, stop_event):
    """Асинхронная функция для мониторинга данных"""
    values = {"Battery": "—", "Temp": "—", "TOF": "—", "Weight": "—"}
    while not stop_event.is_set():
        line = await proc.stdout.readline()  # Асинхронно читаем строку
        if not line:
            break
        match = LOG_PATTERN.search(line)
        if match:
            key, val = match.groups()
            values[key] = val
            draw_log_table(values)
    proc.terminate()
    clear()

async def show_serial_data():
    """Функция для отображения серийных данных"""
    clear()

    stop_event = asyncio.Event()

    proc = await asyncio.create_subprocess_exec(
        "platformio", "device", "monitor", "--baud", "115200", "--port", "/dev/ttyS0",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    # Асинхронно мониторим данные
    asyncio.create_task(monitor_serial_data(proc, stop_event))

    while not btn_back.is_pressed:
        await asyncio.sleep(0.1)  # Ожидаем нажатия кнопки

    stop_event.set()  # Останавливаем мониторинг
    await proc.wait()  # Ждем завершения процесса

    clear()

    return "main"


