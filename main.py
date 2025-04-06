from menu import start_main_menu
from flash_menu import start_flash_menu
import time

# Глобальная переменная текущего меню
current_menu = None

# Функции переключения меню
def go_to_main_menu():
    global current_menu
    current_menu = lambda: start_main_menu(go_to_flash_menu)

def go_to_flash_menu():
    global current_menu
    current_menu = lambda: start_flash_menu(go_to_main_menu)

# Запускаем с главного меню
go_to_main_menu()

# Основной цикл
while True:
    current_menu()  # вызываем активное меню
    time.sleep(0.1)  # не грузим проц
