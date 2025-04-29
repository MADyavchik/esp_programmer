from menu import start_main_menu
from menu import start_flash_menu
from serial_log_viewer import show_serial_data
from git_update import start_git_update
from mac_view import show_mac_address
from menu import start_settings_menu
import asyncio

# Маппинг меню
menu_map = {
    "main": start_main_menu,
    "flash": start_flash_menu,
    "log": show_serial_data,
    "update": start_git_update,
    "mac": show_mac_address,
    "settings": start_settings_menu,  # async
}

async def run_menu_loop():
    stack = ["main"]  # Начинаем с главного меню

    while stack:
        current = stack[-1]  # Получаем текущее меню
        handler = menu_map.get(current)  # Ищем обработчик для текущего меню

        if not handler:
            print(f"⚠️ Нет обработчика для '{current}', выходим.")
            stack.pop()
            continue

        result = await handler()  # Вызовем обработчик

        if result is None:
            # Возврат назад
            print(f"Returning from {current} menu")  # Логируем возврат
            stack.pop()
        elif result == "exit":
            # Явный выход (можно использовать в любом меню)
            break
        else:
            # Переход в подменю
            print(f"Entering {result} menu")  # Логируем переход
            stack.append(result)  # Добавляем новое меню в стек
