# system_status.py
import subprocess
import time
from oled_ui import update_status_data

def get_battery_status():
    try:
        raise Exception("нет данных")
    except Exception:
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
        time.sleep(20)


