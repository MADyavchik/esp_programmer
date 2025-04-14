# system_status.py
import subprocess
import time
from oled_ui import update_status_data

# Добавляем поддержку INA219
from adafruit_ina219 import INA219
import board
import busio

# Настройка I2C и инициализация INA219
i2c_bus = busio.I2C(board.SCL, board.SDA)
ina = INA219(i2c_bus)

from collections import deque

voltage_history = deque(maxlen=5)  # храним последние 5 измерений

def get_battery_status():
    try:
        voltage = ina.bus_voltage + ina.shunt_voltage
        voltage_history.append(voltage)
        avg_voltage = sum(voltage_history) / len(voltage_history)

        percent = (avg_voltage - 3.0) / (4.2 - 3.0) * 100
        percent = max(0, min(100, percent))
        return f"{int(percent)}%"
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
        return f"{'|' * signal_bars + '-' * (5-signal_bars)} ({signal_level})"
    else:
        return "Signal: -----"

# 🌙 Фоновая функция для обновления данных
def status_updater():
    while True:
        battery = get_battery_status()
        wifi = get_wifi_status()
        update_status_data(battery, wifi)
        time.sleep(1)

