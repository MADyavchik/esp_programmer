# menu.py

import os
import sys
import time
import asyncio

from buttons import setup_buttons, safe_async
from oled_ui import draw_menu, clear, show_message
from utils import log_async
from esp_flasher import flash_firmware
from printer_functions import printer_connection, connect_to_printer, disconnect_from_printer

# --- Глобальные переменные ---

# Главное меню
MAIN_MENU_ITEMS = ["FLASH", "UPDATE", "LOG", "SETTINGS"]
FLASH_ITEMS = ["Universal", "Master", "Repeater", "Sens_SW", "Sens_OLD"]
VISIBLE_LINES = 4


# --- Вспомогательные функции ---

def reboot_pi():
    show_message("Reboot...")
    time.sleep(1)
    clear()
    os.execv(sys.executable, [sys.executable] + sys.argv)

# --- Меню: Главное ---

@log_async
async def start_main_menu():
    selected = [0]    # выбранный пункт в полном списке
    cursor = [0]      # положение курсора на экране (0..visible_lines-1)
    scroll = [0]      # откуда начинается отображение
    selected_result = [None]
    last_redraw = [time.time()]

    def draw():
        draw_menu(
            items=MAIN_MENU_ITEMS,
            selected_index=scroll[0] + cursor[0],  # передаем реальный индекс
            scroll=scroll[0],
            visible_lines=VISIBLE_LINES,
            highlight_color="yellow",
            show_back_button=False
        )

    def up():
        selected[0] = (selected[0] - 1) % len(MAIN_MENU_ITEMS)

        if cursor[0] > 0:
            cursor[0] -= 1
        else:
            scroll[0] -= 1
            if scroll[0] < 0:
                scroll[0] = max(0, len(MAIN_MENU_ITEMS) - VISIBLE_LINES)
                cursor[0] = min(VISIBLE_LINES - 1, len(MAIN_MENU_ITEMS) - 1)

        draw()
        last_redraw[0] = time.time()

    def down():
        selected[0] = (selected[0] + 1) % len(MAIN_MENU_ITEMS)

        if cursor[0] < min(VISIBLE_LINES - 1, len(MAIN_MENU_ITEMS) - 1):
            cursor[0] += 1
        else:
            scroll[0] += 1
            if scroll[0] > len(MAIN_MENU_ITEMS) - VISIBLE_LINES:
                scroll[0] = 0
                cursor[0] = 0

        draw()
        last_redraw[0] = time.time()

    def back():
        selected_result[0] = None

    def back_hold():
        reboot_pi()

    def select():
        selected_result[0] = MAIN_MENU_ITEMS[selected[0]].lower()
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

# --- Меню: Прошивка ---

@log_async
async def start_flash_menu():
    selected = [0]    # выбранный элемент по списку
    cursor = [0]      # положение курсора на экране (0..visible_lines-1)
    scroll = [0]      # откуда начинается отображение
    next_menu = ["flash"]
    last_redraw = [time.time()]


    def draw_flash():
        draw_menu(
            items=FLASH_ITEMS,
            selected_index=scroll[0] + cursor[0],
            scroll=scroll[0],
            visible_lines=VISIBLE_LINES,
            highlight_color="red",
            show_back_button=False
        )

    def up():
        selected[0] = (selected[0] - 1) % len(FLASH_ITEMS)

        if cursor[0] > 0:
            cursor[0] -= 1
        else:
            scroll[0] -= 1
            if scroll[0] < 0:
                scroll[0] = max(0, len(FLASH_ITEMS) - VISIBLE_LINES)
                cursor[0] = min(VISIBLE_LINES - 1, len(FLASH_ITEMS) - 1)

        draw_flash()
        last_redraw[0] = time.time()

    def down():
        selected[0] = (selected[0] + 1) % len(FLASH_ITEMS)

        if cursor[0] < min(VISIBLE_LINES - 1, len(FLASH_ITEMS) - 1):
            cursor[0] += 1
        else:
            scroll[0] += 1
            if scroll[0] > len(FLASH_ITEMS) - VISIBLE_LINES:
                scroll[0] = 0
                cursor[0] = 0

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

# --- Меню: Настройки (Принтер) ---

@log_async
async def start_settings_menu():
    await asyncio.sleep(0.1)
    menu_items = ["Print: ?"]
    selected = [0]
    selected_result = [None]
    last_redraw = [0]

    def refresh_labels():
        menu_items[0] = f"Print: {'On' if printer_connection['connected'] else 'Off'}"

    def draw():
        refresh_labels()
        draw_menu(
            items=menu_items,
            selected_index=selected[0],
            scroll=selected[0],
            visible_lines=1,
            highlight_color="yellow",
            show_back_button=False
        )

    async def select():
        if printer_connection["connected"]:
            await disconnect_from_printer()
        else:
            await connect_to_printer()
        draw()

    def up():
        selected[0] = (selected[0] - 1) % len(menu_items)
        draw()

    def down():
        selected[0] = (selected[0] + 1) % len(menu_items)
        draw()

    def back():
        selected_result[0] = "main"

    setup_buttons(up, down, back, lambda: safe_async(select))

    draw()
    last_redraw[0] = time.time()

    while selected_result[0] is None:
        await asyncio.sleep(0.1)
        if time.time() - last_redraw[0] > 3:
            draw()
            last_redraw[0] = time.time()

    return selected_result[0]
