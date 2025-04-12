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
