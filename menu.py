# menu.py
import time
import os
import sys
import asyncio

from buttons import setup_buttons
from oled_ui import draw_menu, clear, show_message
from utils import log_async
from esp_flasher import flash_firmware

# --- Переменные ---
FLASH_ITEMS = ["Universal", "Master", "Repeater", "Sens_SW", "Sens_OLD"]
VISIBLE_LINES = 4

# --- Вспомогательные функции ---
def reboot_pi():
    show_message("Reboot...")
    time.sleep(1)
    clear()
    os.execv(sys.executable, [sys.executable] + sys.argv)

# --- Главное меню ---
@log_async
async def start_main_menu():
    menu_items = ["FLASH", "UPDATE", "LOG", "SETTINGS"]
    selected = [0]
    selected_result = [None]
    last_redraw = [time.time()]

    def draw():
        draw_menu(
            items=menu_items,
            selected_index=selected[0],
            scroll=0,
            visible_lines=None,
            highlight_color="yellow",
            show_back_button=False
        )

    def up():
        selected[0] = (selected[0] - 1) % len(menu_items)
        draw()
        last_redraw[0] = time.time()

    def down():
        selected[0] = (selected[0] + 1) % len(menu_items)
        draw()
        last_redraw[0] = time.time()

    def back():
        selected_result[0] = None

    def back_hold():
        reboot_pi()

    def select():
        selected_result[0] = menu_items[selected[0]].lower()
        draw()
        last_redraw[0] = time.time()

    def up_hold():
        selected_result[0] = "mac"

    setup_buttons(up, down, back, select, up_hold_action=up_hold, back_hold_action=back_hold)

    draw()

    while selected_result[0] is None:
        await asyncio.sleep(0.1)
        if time.time() - last_redraw[0] >= 1:
            draw()
            last_redraw[0] = time.time()

    return selected_result[0]

# --- Меню прошивки ---
@log_async
async def start_flash_menu():
    selected = [0]
    scroll = [0]
    next_menu = ["flash"]
    last_redraw = [time.time()]

    def draw_flash():
        draw_menu(
            items=FLASH_ITEMS,
            selected_index=selected[0],
            scroll=scroll[0],
            visible_lines=VISIBLE_LINES,
            highlight_color="red",
            show_back_button=False
        )

    def up():
        selected[0] = (selected[0] - 1) % len(FLASH_ITEMS)
        scroll[0] = selected[0]
        draw_flash()
        last_redraw[0] = time.time()

    def down():
        selected[0] = (selected[0] + 1) % len(FLASH_ITEMS)
        scroll[0] = selected[0]
        draw_flash()
        last_redraw[0] = time.time()

    def back():
        next_menu[0] = "main"

    async def select():
        name = FLASH_ITEMS[selected[0]]
        print(f"▶ Выбрана прошивка: {name}")
        clear()
        result = await flash_firmware(name.lower())
        print(f"◀ Возвращаемся в меню: {result}")
        next_menu[0] = result or "flash"
        draw_flash()
        last_redraw[0] = time.time()

    setup_buttons(up, down, back, select)

    draw_flash()

    while next_menu[0] == "flash":
        await asyncio.sleep(0.1)
        if time.time() - last_redraw[0] >= 1:
            draw_flash()
            last_redraw[0] = time.time()

    return next_menu[0]
