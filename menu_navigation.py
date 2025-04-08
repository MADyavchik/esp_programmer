# menu_navigation.py
from menu import start_main_menu
from flash_menu import start_flash_menu

menu_map = {
    "main": start_main_menu,
    "flash": start_flash_menu,
}

def run_menu_loop():
    current = "main"

    while current:
        next_menu = menu_map[current]()
        current = next_menu
