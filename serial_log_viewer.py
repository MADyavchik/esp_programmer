import asyncio
import subprocess
from utils import log_async
import re
from oled_ui import draw_log_table, clear
from buttons import btn_back
from buttons import setup_buttons
from oled_ui import show_message

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
        try:
            line = await asyncio.wait_for(proc.stdout.readline(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            print(f"Readline error: {e}")
            break

        if not line:
            print("🔌 Порт закрылся")
            break

        line = line.decode("utf-8", errors="ignore").strip()
        print(f"Received line: {line}")

        # 1. Стандартный парсинг
        match = LOG_PATTERN.search(line)
        if match:
            key, val = match.groups()
            if key in values:
                values[key]["value"] = val
                values[key]["status"] = "white"
                draw_log_table(values)
            continue

        # 2. Дополнительный парсинг
        for key, pattern in EXTRA_PATTERNS.items():
            match = pattern.search(line)
            if match:
                if len(match.groups()) == 2:
                    status, value = match.groups()
                    values[key]["value"] = f"{value}"
                    values[key]["status"] = "lime" if status == "OK" else ("red" if status == "FAIL" else "white")
                else:
                    value = match.group(1)
                    values[key]["value"] = value
                    values[key]["status"] = "white"
                draw_log_table(values)
                break


@log_async
async def show_serial_data():
    """Функция для отображения серийных данных"""
    clear()
    stop_event = asyncio.Event()

    # Попытка запуска
    try:
        proc = await asyncio.create_subprocess_exec(
            "platformio", "device", "monitor", "--baud", "115200", "--port", "/dev/ttyS0",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    except Exception as e:
        show_message(f"Ошибка запуска:\n{e}")
        await asyncio.sleep(2)
        clear()
        return "flash"

    # Старт логгирования stderr
    asyncio.create_task(log_stderr(proc))

    # Кнопка назад
    def handle_back():
        stop_event.set()

    setup_buttons(None, None, handle_back, None)

    # Старт мониторинга
    monitor_task = asyncio.create_task(monitor_serial_data(proc, stop_event))

    # Ждём выхода
    await stop_event.wait()

    # Завершаем таск
    if not monitor_task.done():
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

    # Завершаем процесс
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
        try:
            line = await asyncio.wait_for(proc.stderr.readline(), timeout=1.0)
            if not line:
                break  # процесс завершился или stderr закрылся
            print(f"⚠️ STDERR: {line.decode().strip()}")
        except asyncio.TimeoutError:
            continue  # просто ждём следующую порцию stderr
        except Exception as e:
            print(f"❌ log_stderr error: {e}")
            break



