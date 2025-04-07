# menu.py
import time
from luma.core.render import canvas
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import ImageFont
import os
from buttons import setup_buttons
from git_update import update_repo  # <-- функция обновления

# Настройка дисплея
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except:
    font = ImageFont.load_default()

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
    device.show()  # Обновляем экран, чтобы он реально очистился
    os.system("sudo reboot")

# Основная функция запуска главного меню
def start_main_menu(go_to_flash_menu):
    draw_menu()

    def up():
        selected[0] = (selected[0] - 1) % len(menu_items)
        draw_menu()

    def down():
        selected[0] = (selected[0] + 1) % len(menu_items)
        draw_menu()

    def back():
        selected[0] = 0
        draw_menu()

    def select():
        if selected[0] == 0:
            go_to_flash_menu()  # переход в подменю прошивок
        else:
            update_repo()  # запуск обновления

    setup_buttons(up, down, back, select, back_hold_action=reboot_pi)
