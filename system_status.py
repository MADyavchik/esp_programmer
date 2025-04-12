#system_status.py
import subprocess

def get_battery_status():
    try:
        # Пример: получить напряжение с АЦП (здесь пока фиктивно)
        # voltage = read_voltage_somehow()
        # percentage = voltage_to_percent(voltage)
        # return f"{percentage}%"

        # Сейчас просто эмуляция: если модуль не подключен — "--%"
        raise Exception("нет данных")
    except Exception:
        return "--%"


def get_wifi_signal():
    try:
        # Получаем информацию о сигнале с помощью iwconfig
        result = subprocess.run(['iwconfig', 'wlan0'], capture_output=True, text=True)
        signal_line = [line for line in result.stdout.splitlines() if "Signal level" in line]

        if signal_line:
            # Извлекаем значение сигнала из строки
            signal_level = int(signal_line[0].split("Signal level=")[1].split(" dBm")[0])
            return signal_level
        else:
            return None
    except Exception as e:
        print(f"Ошибка при получении уровня сигнала Wi-Fi: {e}")
        return None


def signal_to_bars(signal_level):
    if signal_level is None:
        return 0  # Нет сигнала

    # Преобразуем уровень сигнала в деления
    if signal_level <= -100:
        return 0  # Очень слабый сигнал
    elif signal_level >= -50:
        return 5  # Отличный сигнал
    else:
        return int((signal_level + 100) / 10)  # Масштабируем сигнал в диапазоне от -100 до 0


def get_wifi_status():
    signal_level = get_wifi_signal()
    if signal_level is not None:
        signal_bars = signal_to_bars(signal_level)
        return f"Signal: {'|' * signal_bars} ({signal_level} dBm)"
    else:
        return "Signal: --"


