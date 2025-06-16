import asyncio
import subprocess
from utils import log_async
import re
from oled_ui import draw_log_table, clear
from buttons import btn_back
from buttons import setup_buttons
from oled_ui import show_message

import time

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
    last_line_time = time.time()

    while not stop_event.is_set():
        try:
            line = await asyncio.wait_for(proc.stdout.readline(), timeout=1.0)

            if not line:
                print("🔌 Порт закрылся")
                show_message("Disconnect..")
                stop_event.set()
                break

            line = line.decode("utf-8", errors="ignore").strip()

            # 🛑 Пропускаем служебные строки
            if line.startswith('---'):
                print(f"⚙️ Служебная строка: {line}")
                continue

            print(f"Received line: {line}")
            last_line_time = time.time()

            # Стандартный парсинг
            match = LOG_PATTERN.search(line)
            if match:
                key, val = match.groups()
                if key in values:
                    values[key]["value"] = val
                    values[key]["status"] = "white"
                    draw_log_table(values)
                continue

            # Доп. парсинг
            for key, pattern in EXTRA_PATTERNS.items():
                match = pattern.search(line)
                if match:
                    if len(match.groups()) == 2:
                        status, value = match.groups()
                        values[key]["value"] = f"{value}"
                        values[key]["status"] = (
                            "lime" if status == "OK"
                            else "red" if status == "FAIL"
                            else "white"
                        )
                    else:
                        value = match.group(1)
                        values[key]["value"] = value
                        values[key]["status"] = "white"
                    draw_log_table(values)
                    break

        except asyncio.TimeoutError:
            if time.time() - last_line_time > 5:
                print("❌ Нет данных с платы слишком долго — считаем, что отключена")
                show_message("Нет связи")
                stop_event.set()
                break
            continue

        except Exception as e:
            print(f"Readline error: {e}")
            stop_event.set()
            break


@log_async
async def show_serial_data():
    clear()
    stop_event = asyncio.Event()

    try:
        proc = await asyncio.create_subprocess_exec(
            "platformio", "device", "monitor", "--baud", "115200", "--port", "/dev/ttyS0",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    except Exception as e:
        print(f"❌ Не удалось запустить monitor: {e}")
        show_message("Ошибка запуска monitor")
        await asyncio.sleep(2)
        return "flash"

    # stderr лог
    asyncio.create_task(log_stderr(proc, stop_event))

    # Назначаем кнопку "Назад"
    def handle_back():
        print("⬅️ Кнопка назад нажата")
        stop_event.set()

    setup_buttons(None, None, handle_back, None)

    monitor_task = asyncio.create_task(monitor_serial_data(proc, stop_event))

    # Ждем выхода из логгера
    await stop_event.wait()

    # Пробуем завершить процесс
    if proc.returncode is None:
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=3)
        except asyncio.TimeoutError:
            proc.kill()

    # Дождаться завершения задачи
    if not monitor_task.done():
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

    clear()
    return "flash"

# Функция логгирования ошибок
async def log_stderr(proc, stop_event):
    while True:
        try:
            line = await asyncio.wait_for(proc.stderr.readline(), timeout=1.0)
            if not line:
                break
            text = line.decode(errors="ignore").strip()
            print(f"⚠️ STDERR: {text}")
            if "disconnected" in text.lower() or "unavailable" in text.lower():
                print("🛑 Устройство отключено!")
                show_message("Disconnected")
                stop_event.set()
                break
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            print(f"❌ log_stderr error: {e}")
            break



