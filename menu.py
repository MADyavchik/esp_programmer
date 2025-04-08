# menu.py
# Главное меню
from luma.core.render import canvas
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from PIL import ImageFont
from buttons import setup_buttons
from git_update import update_repo
import time
import os

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

menu_items = ["FLASH", "UPDATE"]
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

def start_main_menu():
    draw_menu()
    selected_result = [None]

    def up(): selected[0] = (selected[0] - 1) % len(menu_items); draw_menu()
    def down(): selected[0] = (selected[0] + 1) % len(menu_items); draw_menu()
    def back(): selected_result[0] = None
    def select():
        if selected[0] == 0:
            selected_result[0] = "flash"
        else:
            update_repo()

    setup_buttons(up, down, back, select, reboot_pi)

    # Ожидаем, пока пользователь что-то выберет
    while selected_result[0] is None:
        time.sleep(0.1)

    return selected_result[0]
