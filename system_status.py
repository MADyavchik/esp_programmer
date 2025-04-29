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

MIN_VOLTAGE = 3.0     # Минимальное напряжение (0%)
MAX_VOLTAGE = 4.2     # Максимальное напряжение (100%)
CHANGE_THRESHOLD = 1  # Порог отображения изменений (в процентах)

charging_icon = [""]  # Будем обновлять это значение в status_updater


PORT = "/dev/ttyS0"


def is_charging():
    try:
        current = ina.current  # мА
        #print(f"[INA219] Current = {ina.current} мА")
        return current < -5  # Зарядка: ток входит в батарею (можешь поэкспериментировать с порогом)
    except Exception as e:
        print(f"[INA219] Ошибка при чтении тока: {e}")
        return False


def get_battery_status():
    try:
        voltage = ina.bus_voltage + ina.shunt_voltage
        voltage_history.append(voltage)

        if len(voltage_history) < voltage_history.maxlen:
            return "--%"

        median_voltage = statistics.median(voltage_history)

        percent = (median_voltage - MIN_VOLTAGE) / (MAX_VOLTAGE - MIN_VOLTAGE) * 100
        percent = max(0, min(100, percent))
        rounded_percent = int(percent)

        if last_percent[0] is None or abs(rounded_percent - last_percent[0]) >= CHANGE_THRESHOLD:
            last_percent[0] = rounded_percent

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
CHECK_INTERVAL = 10  # секунд
last_check_time = 0

baseline_current = 300
CURRENT_DELTA_THRESHOLD = 50  # мА, на сколько должен увеличиться ток

def is_esp_powered_by_current():
    global baseline_current
    try:
        current = ina.current  # в мА

        if baseline_current is None:
            baseline_current = current
            print(f"[INA219] Базовый ток установлен: {baseline_current:.1f} мА")
            return False

        delta = current - baseline_current
        print(f"[INA219] Текущий ток: {current:.1f} мА, Δ: {delta:.1f} мА")

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
            mac = get_mac_address()
            if mac:
                print(f"✅ Обнаружена ESP: {mac}")
                connected_state["connected"] = True
                connected_state["mac"] = mac

# Обновлённая фоновая функция
def status_updater():
    while True:
        battery = get_battery_status()
        wifi = get_wifi_status()
        charging = is_charging()

        check_esp_connection()

        if connected_state["connected"]:
            esp_status = f"ESP"
        else:
            esp_status = "   "

        update_status_data(battery, wifi, esp_status, charging)
        time.sleep(1)
