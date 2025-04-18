# flash_menu.py

from buttons import setup_buttons
from esp_flasher import flash_firmware
import time
import asyncio

from oled_ui import clear  # Добавь это, если не было
from oled_ui import draw_flash_menu  # добавить импорт


items = ["Universal", "Master", "Repeater", "Sens_SW", "Sens_OLD"]
selected = [0]
scroll = [0]
VISIBLE_LINES = 2

draw_flash_menu(items, selected[0], scroll[0], VISIBLE_LINES)

async def start_flash_menu():
    clear()
    draw_flash_menu(items, selected[0], scroll[0], VISIBLE_LINES)

    next_menu = ["flash"]

    def up():
        selected[0] = (selected[0] - 1) % len(items)
        scroll[0] = selected[0]
        draw_flash_menu(items, selected[0], scroll[0], VISIBLE_LINES)

    def down():
        selected[0] = (selected[0] + 1) % len(items)
        scroll[0] = selected[0]
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
        await asyncio.sleep(0.1)

    return next_menu[0]
