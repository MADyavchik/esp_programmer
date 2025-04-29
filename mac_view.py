import time
import asyncio
from utils import log_async
from oled_ui import clear, draw_mac_qr, draw_mac_address
from esp_flasher import get_mac_address
from buttons import btn_back
from buttons import setup_buttons
from printer_functions import print_mac_address
from menu import printer_connection

@log_async
async def show_mac_address():
    clear()
    setup_buttons(None, None, None, None)

    mac = get_mac_address()
    #draw_mac_address(mac)
    draw_mac_qr(mac)

    async def print_mac():
        # Проверяем, подключен ли принтер
        if printer_connection.get("connected", False):  # Проверка флага подключения
            printer = printer_connection.get("printer")  # Получаем принтер из глобального состояния
            if printer:
                print(f"Принтер подключен: {printer_connection['device'].name} ({printer_connection['device'].address})")
                await print_mac_address(printer, mac)  # Печатаем MAC-адрес
            else:
                print("⚠️ Принтер не найден.")


    # Используем безопасный асинхронный вызов с кнопкой
    from buttons import safe_async
    safe_async(print_mac)

    # Ждем, пока не нажмут кнопку назад
    while not btn_back.is_pressed:
        await asyncio.sleep(0.1)
    while btn_back.is_pressed:
        await asyncio.sleep(0.1)

    return "main"
