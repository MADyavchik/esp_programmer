from menu import start_main_menu
from flash_menu import start_flash_menu
from serial_log_viewer import show_serial_data
from git_update import start_git_update
from mac_view import show_mac_address
from settings import start_settings_menu
import asyncio

menu_map = {
    "main": start_main_menu,
    "flash": start_flash_menu,
    "log": show_serial_data,
    "update": start_git_update,
    "mac": show_mac_address,
    "settings": start_settings_menu,  # async
}

async def run_menu_loop():
    current = "main"
    while current:
        next_menu = menu_map[current]()
        if asyncio.iscoroutine(next_menu):
            next_menu = await next_menu
        current = next_menu
