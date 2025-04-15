# menu.py
from luma.core.render import canvas
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from PIL import ImageFont
from buttons import setup_buttons

from esp_flasher import get_mac_address
import time
import os
from oled_ui import clear
from buttons import btn_back
from system_status import get_battery_status, get_wifi_status
from oled_ui import draw_status_bar
from oled_ui import draw_main_menu


serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

menu_items = ["FLASH", "UPDATE", "LOG"]
selected = [0]
scroll = [0]
VISIBLE_LINES = 2  # Только 2 пункта меню под статусом

def draw_menu():
    draw_main_menu(menu_items, selected[0], scroll[0], VISIBLE_LINES)

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
    last_redraw = [time.time()]

    def up():
        if selected[0] > 0:
            selected[0] -= 1
            scroll[0] = selected[0]  # курсор всегда вверху, меняется scroll
        draw_menu()
        last_redraw[0] = time.time()

    def down():
        if selected[0] < len(menu_items) - 1:
            selected[0] += 1
            scroll[0] = selected[0]  # курсор всегда вверху, меняется scroll
        draw_menu()
        last_redraw[0] = time.time()

    def back():
        selected_result[0] = None

    def back_hold():
        reboot_pi()

    def select():
        if selected[0] == 0:  # FLASH
            selected_result[0] = "flash"
        elif selected[0] == 1:  # UPDATE
            selected_result[0] = "update"
        elif selected[0] == 2:  # LOG
            selected_result[0] = "log"
        draw_menu()
        last_redraw[0] = time.time()

    def up_hold():
        display_mac_address()
        last_redraw[0] = time.time()

    setup_buttons(up, down, back, select, up_hold_action=up_hold, back_hold_action=back_hold)

    while selected_result[0] is None:
        time.sleep(0.1)

        # 🔁 Автообновление меню каждые 3 секунды
        if time.time() - last_redraw[0] >= 3:
            draw_menu()
            last_redraw[0] = time.time()

    return selected_result[0]
