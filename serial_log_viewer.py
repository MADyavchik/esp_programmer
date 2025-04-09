# serial_log_viewer.py
import subprocess
import re
import time
from threading import Thread
from oled_ui import draw_log_table, clear
from buttons import btn_back
from menu import draw_menu  # Импортируем функцию для отрисовки меню
import threading

LOG_PATTERN = re.compile(r"(Battery|Temp|TOF|Weight):\s*(-?\d+)")

def monitor_serial_data(proc, stop_event):
    """Функция для мониторинга данных в отдельном потоке"""
    try:
        values = {"Battery": "—", "Temp": "—", "TOF": "—", "Weight": "—"}
        for line in proc.stdout:
            if stop_event.is_set():  # Прерывание потока, если stop_event активирован
                break
            match = LOG_PATTERN.search(line)
            if match:
                key, val = match.groups()
                values[key] = val
                draw_log_table(values)

    except Exception as e:
        print(f"Ошибка чтения монитора: {e}")

    proc.terminate()  # Завершаем процесс, если кнопка нажата
    clear()

def show_serial_data():
    clear()

    # Создаем объект для отслеживания остановки потока
    stop_event = threading.Event()

    # Запускаем subprocess с pio monitor в отдельном потоке
    proc = subprocess.Popen(
        ["platformio", "device", "monitor", "--baud", "115200", "--port", "/dev/ttyAMA1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    # Запускаем функцию мониторинга в новом потоке
    monitor_thread = Thread(target=monitor_serial_data, args=(proc, stop_event))
    monitor_thread.start()

    # Ожидаем нажатия кнопки "Back"
    while not btn_back.is_pressed:
        time.sleep(0.1)

    # Как только кнопка нажата, останавливаем поток и прерываем мониторинг
    stop_event.set()
    proc.terminate()  # Завершаем процесс
    monitor_thread.join()  # Дожидаемся завершения потока мониторинга

    # Очистка экрана
    clear()

    # Вызов функции для отрисовки главного меню
    draw_menu()  # Теперь меню будет отрисовано после выхода из режима логирования


