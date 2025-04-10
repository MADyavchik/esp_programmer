# menu.py
# Главное меню
from luma.core.render import canvas
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from PIL import ImageFont
from buttons import setup_buttons
from git_update import update_repo
from esp_flasher import get_mac_address
import time
import os
from oled_ui import clear
from buttons import btn_back

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

menu_items = ["FLASH", "UPDATE", "LOG"]
selected = [0]

def draw_menu():
    with canvas(device) as draw:
        for i, item in enumerate(menu_items):
            prefix = "> " if i == selected[0] else "  "
            draw.text((10, 10 + i * 20), prefix + item, font=font, fill="white")

def reboot_pi():
    with canvas(device) as draw:
        draw.text((10, 10), "Перезагрузка...", font=font, fill="white")
    time.sleep(1)
    device.clear()
    os.system("sudo reboot")

def display_mac_address():
    clear()
    mac = get_mac_address()

    with canvas(device) as draw:
        if mac:
            draw.text((0, 0), "MAC Address:", font=font, fill="white")
            draw.text((0, 30), mac, font=font, fill="white")
        else:
            draw.text((10, 10), "Error getting MAC", font=font, fill="white")

    # Ждём, пока пользователь нажмёт "Back"
    while not btn_back.is_pressed:
        time.sleep(0.1)

    while btn_back.is_pressed:  # дождись отпускания
        time.sleep(0.1)

    draw_menu()

def start_main_menu():
    draw_menu()
    selected_result = [None]

    def up():
        selected[0] = (selected[0] - 1) % len(menu_items)
        draw_menu()

    def down():
        selected[0] = (selected[0] + 1) % len(menu_items)
        draw_menu()

    def back():
        selected_result[0] = None

    def back_hold():
        reboot_pi()

    def select():
        # Действие при выборе элемента меню
        if selected[0] == 0:  # Пункт "FLASH"
            selected_result[0] = "flash"
        elif selected[0] == 1:  # Пункт "UPDATE"
            update_repo()
        elif selected[0] == 2:  # Пункт "LOG"
            from serial_log_viewer import show_serial_data
            show_serial_data()

    # Добавляем функцию для зажатия кнопки up на 3 секунды
    def up_hold():
        # Показать MAC-адрес, если кнопка up зажата
        display_mac_address()

    # Устанавливаем обработчики кнопок
    setup_buttons(up, down, back, select, up_hold_action=up_hold, back_hold_action=back_hold)

    # Ожидаем, пока пользователь не сделает выбор
    while selected_result[0] is None:
        time.sleep(0.1)

    return selected_result[0]
