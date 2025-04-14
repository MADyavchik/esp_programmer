from menu import start_main_menu
from flash_menu import start_flash_menu
from serial_log_viewer import show_serial_data
from git_update import start_git_update  # <--- добавили

menu_map = {
    "main": start_main_menu,
    "flash": start_flash_menu,
    "log": show_serial_data,
    "update": start_git_update,  # <--- добавили
}

def run_menu_loop():
    current = "main"

    while current:
        next_menu = menu_map[current]()
        current = next_menu
