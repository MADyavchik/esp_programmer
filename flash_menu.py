# flash_menu.py

from buttons import setup_buttons
from esp_flasher import flash_firmware
import time
import asyncio

from oled_ui import clear
from oled_ui import draw_menu  # вместо draw_flash_menu
from utils import log_async

items = ["Universal", "Master", "Repeater", "Sens_SW", "Sens_OLD"]
selected = [0]
scroll = [0]
VISIBLE_LINES = 4

def draw_flash():
    draw_menu(
        items=items,
        selected_index=selected[0],
        scroll=scroll[0],
        visible_lines=VISIBLE_LINES,
        highlight_color="red",
        show_back_button=True
    )

@log_async
async def start_flash_menu():
    last_redraw = [time.time()]
    #clear()
    draw_flash()

    next_menu = ["flash"]

    def up():
        selected[0] = (selected[0] - 1) % len(items)
        scroll[0] = selected[0]
        draw_flash()
        last_redraw[0] = time.time()

    def down():
        selected[0] = (selected[0] + 1) % len(items)
        scroll[0] = selected[0]
        draw_flash()
        last_redraw[0] = time.time()

    def back():
        next_menu[0] = "main"

    async def select():
        name = items[selected[0]]
        print(f"▶ Выбрана прошивка: {name}")
        clear()
        result = await flash_firmware(name.lower())
        print(f"◀ Возвращаемся в меню: {result}")
        next_menu[0] = result or "flash"
        draw_flash()
        last_redraw[0] = time.time()

    setup_buttons(up, down, back, select)

    while next_menu[0] == "flash":
        await asyncio.sleep(0.1)
        if time.time() - last_redraw[0] >= 0.1:
            draw_flash()
            last_redraw[0] = time.time()

    return next_menu[0]
