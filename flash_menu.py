# flash_menu.py
from luma.core.render import canvas
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import ImageFont
from buttons import setup_buttons
import time

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except:
    font = ImageFont.load_default()

items = ["FW1", "FW2", "FW3"]
selected = [0]

def draw_flash_menu():
    with canvas(device) as draw:
        for i, item in enumerate(items):
            prefix = "> " if i == selected[0] else "  "
            draw.text((10, 10 + i * 20), prefix + item, font=font, fill="white")

def start_flash_menu(go_to_main_menu):
    draw_flash_menu()

    def up():
        selected[0] = (selected[0] - 1) % len(items)
        draw_flash_menu()

    def down():
        selected[0] = (selected[0] + 1) % len(items)
        draw_flash_menu()

    def back():
        go_to_main_menu()  # вернуться в главное меню

    def select():
        print(f"Прошивка: {items[selected[0]]}")
        # Тут можно добавить реальную прошивку по выбору

    setup_buttons(up, down, back, select)
