import asyncio
import subprocess
import re
from oled_ui import draw_log_table, clear
from buttons import btn_back
from buttons import setup_buttons

LOG_PATTERN = re.compile(r"(Battery|Temp|TOF|Weight):\s*(-?\d+)")

async def monitor_serial_data(proc, stop_event):
    """Асинхронная функция для мониторинга данных"""
    values = {"Battery": "—", "Temp": "—", "TOF": "—", "Weight": "—"}

    # Сразу рисуем таблицу с дефолтными значениями
    draw_log_table(values)

    while not stop_event.is_set():
        line = await proc.stdout.readline()  # Асинхронно читаем строку
        if not line:
            break
        line = line.decode('utf-8').strip()  # Декодируем байты в строку
        print(f"Received line: {line}")  # Выводим строку в консоль, чтобы проверить
        match = LOG_PATTERN.search(line)
        if match:
            key, val = match.groups()
            values[key] = val
            print(f"Updated values: {values}")  # Выводим обновленные данные в консоль
            draw_log_table(values)

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

    # Асинхронно мониторим данные
    asyncio.create_task(monitor_serial_data(proc, stop_event))

    while not btn_back.is_pressed:
        await asyncio.sleep(0.1)  # Ожидаем нажатия кнопки

    stop_event.set()  # Останавливаем мониторинг
    await proc.wait()  # Ждем завершения процесса

    clear()

    return "main"


