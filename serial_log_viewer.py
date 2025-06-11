import asyncio
import subprocess
import re
from oled_ui import draw_log_table, clear
from buttons import btn_back
from buttons import setup_buttons

# Старый парсер — не трогаем
LOG_PATTERN = re.compile(r"(Battery|Temp|TOF|Weight):\s*(-?\d+)", re.IGNORECASE)

# Дополнительные паттерны — из новых логов
EXTRA_PATTERNS = {
    "Battery": re.compile(r"BATTERY\s+\[OK\]\s+(\d+)", re.IGNORECASE),
    "Temp": re.compile(r"1WIRE Temperature\s+\[OK\]\s+Temp:\s+(\d+)", re.IGNORECASE),
    "Weight": re.compile(r"WEIGHT\s+\[OK\]\s+Read\s+(-?\d+)", re.IGNORECASE),
    "CPU Temp": re.compile(r"CPU TEMP\s+\[OK\]\s+(\d+)", re.IGNORECASE),
    "DOM.Online": re.compile(r"SSID\s+DOM\.Online\s+RSSI:\s+(-?\d+)", re.IGNORECASE),
}

# Данные для таблицы
values = {
    "Battery": "—",
    "Temp": "—",          # 1WIRE Temp
    "TOF": "—",
    "Weight": "—",
    "CPU Temp": "—",
    "DOM.Online": "—"
}

async def monitor_serial_data(proc, stop_event):
    draw_log_table(values)

    while not stop_event.is_set():
        line = await proc.stdout.readline()
        if not line:
            break
        line = line.decode('utf-8').strip()
        print(f"Received line: {line}")

        # 1. Стандартный парсинг
        match = LOG_PATTERN.search(line)
        if match:
            key, val = match.groups()
            key = key.capitalize()
            values[key] = val
            print(f"Updated values: {values}")
            draw_log_table(values)
            continue

        # 2. Расширенный парсинг
        for key, pattern in EXTRA_PATTERNS.items():
            match = pattern.search(line)
            if match:
                values[key] = match.group(1)
                print(f"Updated extra value: {key} = {values[key]}")
                draw_log_table(values)
                break

    proc.terminate()
    clear()

async def show_serial_data():
    """Функция для отображения серийных данных"""
    clear()

    # Оставляем только кнопку "назад", остальные отключаем
    setup_buttons(None, None, None, None)


    stop_event = asyncio.Event()

    proc = await asyncio.create_subprocess_exec(
        "platformio", "device", "monitor", "--baud", "115200", "--port", "/dev/ttyS0",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

     # 👇 Воткнули сюда
    stderr_line = await proc.stderr.readline()
    if stderr_line:
        print(f"⚠️ PLATFORMIO ERROR: {stderr_line.decode().strip()}")

    # Асинхронно мониторим данные
    asyncio.create_task(monitor_serial_data(proc, stop_event))

    while not btn_back.is_pressed:
        await asyncio.sleep(0.1)  # Ожидаем нажатия кнопки

    stop_event.set()  # Останавливаем мониторинг
    await proc.wait()  # Ждем завершения процесса

    clear()

    return "main"


