import time
import asyncio
from oled_ui import draw_mac_address, clear
from esp_flasher import get_mac_address
from buttons import btn_back
from printer_functions import connect_printer, print_mac_address, disconnect_printer, get_device_by_mac

def show_mac_address():
    clear()
    mac = get_mac_address()
    draw_mac_address(mac)  # Отображаем MAC-адрес на экране

    async def print_mac():
        # Печать MAC-адреса
        device = await get_device_by_mac("01:EC:01:36:C3:86")  # Здесь укажи MAC-адрес своего устройства
        if device:
            print(f"Устройство найдено: {device.name} ({device.address})")
            printer = await connect_printer(device)  # Асинхронно подключаемся к принтеру
            await print_mac_address(printer, mac)   # Печатаем MAC-адрес
            await disconnect_printer(printer)       # Отключаем принтер

    # Запуск асинхронной функции для печати
    asyncio.run(print_mac())

    while not btn_back.is_pressed:
        time.sleep(0.1)
    while btn_back.is_pressed:
        time.sleep(0.1)

    return "main"
