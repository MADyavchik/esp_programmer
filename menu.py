# menu.py
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
from system_status import get_battery_status

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

menu_items = ["FLASH", "UPDATE", "LOG"]
selected = [0]
scroll = [0]
VISIBLE_LINES = 2  # Только 2 пункта меню под статусом

def draw_menu():
    battery_status = get_battery_status()
    with canvas(device) as draw:
        # Статусная строка (пример: батарея, можно заменить потом)
        draw.text((0, 0), f"{battery_status}", font=font, fill="white")

        # Меню начинается с Y = 18, чтобы не наезжать на статус
        for i in range(VISIBLE_LINES):
            index = scroll[0] + i
            if index >= len(menu_items):
                break
            prefix = "> " if index == selected[0] else "  "
            draw.text((10, 18 + i * 20), prefix + menu_items[index], font=font, fill="white")

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

    while not btn_back.is_pressed:
        time.sleep(0.1)
    while btn_back.is_pressed:
        time.sleep(0.1)
    draw_menu()

def start_main_menu():
    draw_menu()
    selected_result = [None]

    def up():
        if selected[0] > 0:
            selected[0] -= 1
            if selected[0] < scroll[0]:
                scroll[0] -= 1
        draw_menu()

    def down():
        if selected[0] < len(menu_items) - 1:
            selected[0] += 1
            if selected[0] >= scroll[0] + VISIBLE_LINES:
                scroll[0] += 1
        draw_menu()

    def back():
        selected_result[0] = None

    def back_hold():
        reboot_pi()

    def select():
        if selected[0] == 0:  # FLASH
            selected_result[0] = "flash"
        elif selected[0] == 1:  # UPDATE
            update_repo()
        elif selected[0] == 2:  # LOG
            from serial_log_viewer import show_serial_data
            show_serial_data()
        draw_menu()

    def up_hold():
        display_mac_address()

    setup_buttons(up, down, back, select, up_hold_action=up_hold, back_hold_action=back_hold)

    while selected_result[0] is None:
        time.sleep(0.1)

    return selected_result[0]
