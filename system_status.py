# system_status.py
import subprocess
import time
from oled_ui import update_status_data
import serial
import logging
from esp_flasher import get_mac_address
import os

# Добавляем поддержку INA219
from adafruit_ina219 import INA219
import board
import busio

# Настройка I2C и инициализация INA219
i2c_bus = busio.I2C(board.SCL, board.SDA)
ina = INA219(i2c_bus)

from collections import deque
import statistics

voltage_history = deque(maxlen=60)
last_percent = [None]  # Используем список, чтобы изменять внутри функции

MIN_VOLTAGE = 3.3     # Минимальное напряжение (0%)
MAX_VOLTAGE = 4.2     # Максимальное напряжение (100%)
CHANGE_THRESHOLD = 1  # Порог отображения изменений (в процентах)

charging_icon = [""]  # Будем обновлять это значение в status_updater


PORT = "/dev/ttyS0"

def voltage_to_percent(v):
    # Значения под нагрузкой (приблизительные)
    lut = [
        (4.20, 100),
        (4.10, 95),
        (4.00, 90),
        (3.92, 80),
        (3.85, 70),
        (3.79, 60),
        (3.75, 50),
        (3.70, 40),
        (3.65, 30),
        (3.60, 20),
        (3.50, 10),
        (3.40, 5),
        (3.30, 0)
    ]
    for voltage, percent in lut:
        if v >= voltage:
            return percent
    return 0


def is_charging():
    try:
        current = ina.current  # мА
        print(f"[INA219] Current = {ina.current} мА")
        return current < -5  # Зарядка: ток входит в батарею (можешь поэкспериментировать с порогом)
    except Exception as e:
        print(f"[INA219] Ошибка при чтении тока: {e}")
        return False


def get_battery_status():
    try:
        voltage = ina.bus_voltage
        voltage_history.append(voltage)

        if len(voltage_history) < voltage_history.maxlen:
            return "--%"

        median_voltage = statistics.median(voltage_history)
        rounded_percent = voltage_to_percent(median_voltage)

        if last_percent[0] is None or abs(rounded_percent - last_percent[0]) >= CHANGE_THRESHOLD:
            last_percent[0] = rounded_percent

        # Предупреждение о падении напряжения
        if median_voltage < 3.3:
            print(f"⚠️ Низкое напряжение: {median_voltage:.2f} В — возможное отключение скоро")

        return f"{last_percent[0]}%"
    except Exception as e:
        print(f"[INA219] Ошибка получения данных: {e}")
        return "--%"


def get_wifi_signal():
    try:
        result = subprocess.run(['iwconfig', 'wlan0'], capture_output=True, text=True)
        signal_line = [line for line in result.stdout.splitlines() if "Signal level" in line]
        if signal_line:
            signal_level = int(signal_line[0].split("Signal level=")[1].split(" dBm")[0])
            return signal_level
    except Exception as e:
        print(f"Wi-Fi error: {e}")
    return None


def signal_to_bars(signal_level):
    if signal_level is None:
        return 0
    if signal_level <= -100:
        return 0
    elif signal_level >= -50:
        return 5
    else:
        return int((signal_level + 100) / 10)


def get_wifi_status():
    signal_level = get_wifi_signal()
    if signal_level is not None:
        signal_bars = signal_to_bars(signal_level)
        #return f"{'|' * signal_bars + '-' * (5-signal_bars)} ({signal_level})"
        return f"{'|' * signal_bars + '-' * (5-signal_bars)}"
    else:
        return "-----"


# 🌙 Фоновая функция для обновления данных
# Добавь в начало (если ещё не добавлено)
connected_state = {"connected": False, "mac": None}
CHECK_INTERVAL = 1  # секунд
last_check_time = 0

CURRENT_WINDOW_SIZE = 10
current_readings = deque(maxlen=CURRENT_WINDOW_SIZE)
baseline_current = None
CURRENT_DELTA_THRESHOLD = 50  # мА

def is_esp_powered_by_current():
    global baseline_current

    try:
        current = ina.current  # мА
        current_readings.append(current)

        if len(current_readings) < CURRENT_WINDOW_SIZE:
            return False  # Недостаточно данных

        median_current = statistics.median(current_readings)

        if baseline_current is None:
            baseline_current = median_current
            print(f"[INA219] Установлен базовый ток (медиана): {baseline_current:.1f} мА")
            return False

        delta = median_current - baseline_current
        print(f"[INA219] Медианный ток: {median_current:.1f} мА, Δ: {delta:.1f} мА")

        return delta > CURRENT_DELTA_THRESHOLD

    except Exception as e:
        print(f"[INA219] Ошибка чтения тока: {e}")
        return False

def check_esp_connection():
    global last_check_time
    now = time.time()
    if now - last_check_time < CHECK_INTERVAL:
        return  # не пора ещё
    last_check_time = now

    if connected_state["connected"]:
        # Проверим по току, не отвалилась ли
        if not is_esp_powered_by_current():
            print("❌ ESP отключена (по току)")
            connected_state["connected"] = False
            connected_state["mac"] = None
    else:
        # Есть ток — пробуем достать MAC
        if is_esp_powered_by_current():

            print(f"✅ Обнаружена ESP")
            connected_state["connected"] = True
            connected_state["mac"] = None

# Обновлённая фоновая функция
def status_updater():
    while True:
        battery = get_battery_status()
        wifi = get_wifi_status()
        charging = is_charging()





        update_status_data(battery, wifi, charging)
        time.sleep(1)
