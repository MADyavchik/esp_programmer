from menu import start_main_menu
from menu import start_flash_menu
from serial_log_viewer import show_serial_data
from git_update import start_git_update
from mac_view import show_mac_address
from menu import start_settings_menu
from screens.print_screen import run_print_screen, run_print_connect
from screens.shotdown_screen import run_shotdown_halt
from oled_ui import inactivity_watcher
import asyncio

# Маппинг меню
menu_map = {
    "main": start_main_menu,
    "flash": start_flash_menu,
    "log": show_serial_data,
    "update": start_git_update,
    "mac": show_mac_address,
    "settings": start_settings_menu,  # async
    "print": run_print_screen,
    "print_connect": run_print_connect,
    "shotdown": run_shotdown_halt,
}

async def run_menu_loop():
    current = "main"

    while current:
        handler = menu_map.get(current)

        if not handler:
            print(f"⚠️ Нет обработчика для '{current}', выходим.")
            break

        # Запускаем параллельно меню и inactivity_watcher
        handler_task = asyncio.create_task(handler())
        watcher_task = asyncio.create_task(inactivity_watcher())

        done, pending = await asyncio.wait(
            [handler_task, watcher_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Получаем результат того, кто завершился первым
        finished_task = list(done)[0]
        result = finished_task.result()

        # Отменяем оставшуюся задачу (если она ещё работает)
        for task in pending:
            task.cancel()

        if result is None:
            print(f"Returning to main menu")
            current = "main"
        elif result == "exit":
            print("Exiting program.")
            break
        else:
            print(f"Entering {result} menu")
            current = result
