# flash_menu.py
from luma.core.render import canvas
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from PIL import ImageFont
from buttons import setup_buttons
from esp_flasher import flash_firmware
import time
import threading
from oled_ui import clear  # Добавь это, если не было
from oled_ui import draw_flash_menu  # добавить импорт

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

items = ["Universal", "Master", "Repeater", "Sens_SW", "Sens_OLD"]
selected = [0]
scroll = [0]
VISIBLE_LINES = 3

draw_flash_menu(items, selected[0], scroll[0], VISIBLE_LINES)

def start_flash_menu():
    clear()
    draw_flash_menu(items, selected[0], scroll[0], VISIBLE_LINES)

    next_menu = ["flash"]

    def up():
        if selected[0] > 0:
            selected[0] -= 1
            if selected[0] < scroll[0]:
                scroll[0] -= 1
        draw_flash_menu(items, selected[0], scroll[0], VISIBLE_LINES)

    def down():
        if selected[0] < len(items) - 1:
            selected[0] += 1
            if selected[0] >= scroll[0] + VISIBLE_LINES:
                scroll[0] += 1
        draw_flash_menu(items, selected[0], scroll[0], VISIBLE_LINES)

    def back():
        next_menu[0] = "main"

    def select():
        name = items[selected[0]]
        print(f"▶ Выбрана прошивка: {name}")
        clear()
        result = flash_firmware(name.lower())
        print(f"◀ Возвращаемся в меню: {result}")
        next_menu[0] = result or "flash"
        draw_flash_menu(items, selected[0], scroll[0], VISIBLE_LINES)

    setup_buttons(up, down, back, select)

    while next_menu[0] == "flash":
        time.sleep(0.1)

    return next_menu[0]
