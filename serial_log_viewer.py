import asyncio
import subprocess
from utils import log_async
import re
from oled_ui import draw_log_table, clear
from buttons import btn_back
from buttons import setup_buttons

# Строго без IGNORECASE для точного совпадения ключей
LOG_PATTERN = re.compile(r"(Battery|Temp|TOF|Weight):\s*(-?\d+)")

# Дополнительные паттерны
EXTRA_PATTERNS = {
    "Battery": re.compile(r"BATTERY\s+\[(OK|FAIL)\]\s+(\d+)"),
    "Temp": re.compile(r"1WIRE Temperature\s+\[(OK|FAIL)\]\s+Temp:\s+(\d+)"),
    "Weight": re.compile(r"WEIGHT\s+\[(OK|FAIL)\]\s+Read\s+(-?\d+)"),
    "CPU Temp": re.compile(r"CPU TEMP\s+\[(OK|FAIL)\]\s+(\d+)"),
    "DOM.Online": re.compile(r"SSID\s+DOM\.Online\s+RSSI:\s+(-?\d+)")
}

# Значения по умолчанию
values = {
    "Battery": {"value": "—", "status": None},
    "Temp": {"value": "—", "status": None},
    "TOF": {"value": "—", "status": None},
    "Weight": {"value": "—", "status": None},
    "CPU Temp": {"value": "—", "status": None},
    "DOM.Online": {"value": "—", "status": None}
}

async def monitor_serial_data(proc, stop_event):
    """Асинхронная функция для мониторинга UART"""
    draw_log_table(values)

    while not stop_event.is_set():
        line = await proc.stdout.readline()
        if not line:
            break

        line = line.decode("utf-8").strip()
        print(f"Received line: {line}")

        # 1. Стандартный парсинг
        match = LOG_PATTERN.search(line)
        if match:
            key, val = match.groups()
            if key in values:
                values[key]["value"] = val
                values[key]["status"] = "white"
                print(f"Updated values: {values}")
                draw_log_table(values)
                continue

        # 2. Дополнительный парсинг
        for key, pattern in EXTRA_PATTERNS.items():
            match = pattern.search(line)
            if match:
                if len(match.groups()) == 2:
                    status, value = match.groups()
                    values[key]["value"] = f"{value}"
                    if status == "OK":
                        values[key]["status"] = f"lime"
                    elif status == "FAIL":
                        values[key]["status"] = f"red"
                    else:
                        values[key]["status"] = f"white"

                else:
                    value = match.group(1)
                    values[key]["value"] = value
                    values[key]["status"] = "white"

                print(f"Updated extra value: {key} = {values[key]}")
                draw_log_table(values)
                break

    proc.terminate()
    clear()
@log_async
async def show_serial_data():
    """Функция для отображения серийных данных"""
    clear()

    stop_event = asyncio.Event()

    proc = await asyncio.create_subprocess_exec(
        "platformio", "device", "monitor", "--baud", "115200", "--port", "/dev/ttyS0",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Логируем stderr
    asyncio.create_task(log_stderr(proc))

    # Задаем кнопку Назад
    def handle_back():
        stop_event.set()

    setup_buttons(None, None, handle_back, None)

    # Запускаем монитор
    monitor_task = asyncio.create_task(monitor_serial_data(proc, stop_event))

    # Ждем завершения
    await stop_event.wait()

    # Ждем завершения таска
    if not monitor_task.done():
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

    # Завершаем subprocess
    try:
        proc.terminate()
        await asyncio.wait_for(proc.wait(), timeout=3)

    except Exception:
        proc.kill()

    clear()
    return "flash"

# Функция логгирования ошибок
async def log_stderr(proc):
    while True:
        line = await proc.stderr.readline()
        if not line:
            break
        print(f"⚠️ STDERR: {line.decode().strip()}")


