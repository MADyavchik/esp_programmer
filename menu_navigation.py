from menu import start_main_menu
from menu import start_flash_menu
from serial_log_viewer import show_serial_data
from git_update import start_git_update
from mac_view import show_mac_address
from menu import start_settings_menu
from printer_functions import print_mac_address
import asyncio

# Маппинг меню
menu_map = {
    "main": start_main_menu,
    "flash": start_flash_menu,
    "log": show_serial_data,
    "update": start_git_update,
    "mac": show_mac_address,
    "settings": start_settings_menu,  # async
    "print": print_mac_address,
}

async def run_menu_loop():
    current = "main"  # Начинаем с главного меню

    while current:
        handler = menu_map.get(current)  # Ищем обработчик для текущего меню

        if not handler:
            print(f"⚠️ Нет обработчика для '{current}', выходим.")
            break

        result = await handler()  # Вызовем обработчик для текущего меню

        if result is None:
            print(f"Returning to main menu")  # Логируем возврат
            current = "main"  # Переводим обратно в главное меню
        elif result == "exit":
            print("Exiting program.")
            break
        else:
            print(f"Entering {result} menu")  # Логируем переход
            current = result  # Переход в подменю
