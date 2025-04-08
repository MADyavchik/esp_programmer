# serial_log_viewer.py
import subprocess
import re
import time
from threading import Thread
from oled_ui import draw_log_table, clear
from buttons import btn_back
from menu import draw_menu  # Импортируем функцию для отрисовки меню

LOG_PATTERN = re.compile(r"(Battery|Temp|TOF|Weight):\s*(-?\d+)")

def monitor_serial_data(proc):
    """Функция для мониторинга данных в отдельном потоке"""
    try:
        values = {"Battery": "—", "Temp": "—", "TOF": "—", "Weight": "—"}
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

    proc.terminate()  # Завершаем процесс, если кнопка нажата
    clear()

def show_serial_data():
    clear()

    # Запускаем subprocess с pio monitor в отдельном потоке
    proc = subprocess.Popen(
        ["platformio", "device", "monitor", "--baud", "115200", "--port", "/dev/ttyS0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    # Запускаем функцию мониторинга в новом потоке
    monitor_thread = Thread(target=monitor_serial_data, args=(proc,))
    monitor_thread.start()

    # Ожидаем нажатия кнопки "Back"
    while not btn_back.is_pressed:
        time.sleep(0.1)

    # Ожидаем, пока кнопка не будет отпущена
    while btn_back.is_pressed:
        time.sleep(0.1)

    # Завершаем работу
    monitor_thread.join()  # Дожидаемся завершения потока мониторинга
    proc.terminate()  # Закрываем процесс
    clear()

    # Вызов функции для отрисовки главного меню
    draw_menu()  # Теперь меню будет отрисовано после выхода из режима логирования


