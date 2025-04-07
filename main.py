from menu import start_main_menu
from flash_menu import start_flash_menu
import time

current_menu = None

def go_to_main_menu():
    global current_menu
    current_menu = lambda: start_main_menu(go_to_flash_menu)

def go_to_flash_menu():
    global current_menu
    current_menu = lambda: start_flash_menu(go_to_main_menu)

go_to_main_menu()  # запускаем главное меню

while True:
    if current_menu:
        current_menu()
        current_menu = None  # не вызываем повторно
    time.sleep(0.1)
