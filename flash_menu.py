# flash_menu.py
from luma.core.render import canvas
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import ImageFont
from buttons import setup_buttons
import time

from esp_flasher import flash_firmware

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except:
    font = ImageFont.load_default()

# МЕНЮ
items = ["Universal", "Master", "Repeater","Sens_SW", "Sens_OLD"]
selected = [0]
scroll = [0]
VISIBLE_LINES = 3  # Кол-во видимых строк

def draw_flash_menu():
    with canvas(device) as draw:
        for i in range(VISIBLE_LINES):
            index = scroll[0] + i
            if index >= len(items): break
            prefix = "> " if index == selected[0] else "  "
            draw.text((10, 10 + i * 20), prefix + items[index], font=font, fill="white")

def start_flash_menu(go_to_main_menu):
    draw_flash_menu()

    def up():
        if selected[0] > 0:
            selected[0] -= 1
            if selected[0] < scroll[0]:
                scroll[0] -= 1
        draw_flash_menu()

    def down():
        if selected[0] < len(items) - 1:
            selected[0] += 1
            if selected[0] >= scroll[0] + VISIBLE_LINES:
                scroll[0] += 1
        draw_flash_menu()

    def back():
        go_to_main_menu()

    def select():
        name = items[selected[0]]
        print(f"Выбрано: {name}")
        flash_firmware(name.lower())  # передаём имя папки

    setup_buttons(up, down, back, select)
