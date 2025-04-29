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

MAIN_MENU_ITEMS = ["FLASH", "UPDATE", "LOG", "SETTINGS"]
FLASH_ITEMS = ["Universal", "Master", "Repeater", "Sens_SW", "Sens_OLD"]
VISIBLE_LINES = 4


# --- Универсальное меню ---

async def run_menu(items, *, visible_lines=4, highlight_color="yellow", show_back_button=False, on_select=None,
                   up_hold_action=None, back_hold_action=None):

    selected = [0]
    cursor = [0]
    scroll = [0]
    result = [None]
    last_redraw = [time.time()]

    def draw():
        draw_menu(
            items=items,
            selected_index=scroll[0] + cursor[0],
            scroll=scroll[0],
            visible_lines=visible_lines,
            highlight_color=highlight_color,
            show_back_button=show_back_button
        )

    async def select():
        index = scroll[0] + cursor[0]
        if on_select:
            await on_select(items[index])
        result[0] = index

    def up():
        selected[0] = (selected[0] - 1) % len(items)
        if cursor[0] > 0:
            cursor[0] -= 1
        else:
            scroll[0] = max(0, scroll[0] - 1)
            if scroll[0] < 0:
                scroll[0] = max(0, len(items) - visible_lines)
                cursor[0] = min(visible_lines - 1, len(items) - 1)
        draw()
        last_redraw[0] = time.time()

    def down():
        selected[0] = (selected[0] + 1) % len(items)
        if cursor[0] < min(visible_lines - 1, len(items) - 1):
            cursor[0] += 1
        else:
            scroll[0] += 1
            if scroll[0] > len(items) - visible_lines:
                scroll[0] = 0
                cursor[0] = 0
        draw()
        last_redraw[0] = time.time()

    def back():
        print("Back button pressed")  # Логирование нажатия кнопки "Назад"
        result[0] = "main"

    # Добавим обработчик зажатия кнопки "Вверх"
    def up_hold():
        print("Up button held!")  # Логируем зажатие кнопки "Вверх"
        if up_hold_action:
            up_hold_action()

    # Задаем кнопки
    setup_buttons(up, down, back, lambda: safe_async(select),
                  up_hold_action=up_hold if up_hold_action else None,
                  back_hold_action=back_hold_action)

    draw()

    while result[0] is None:
        await asyncio.sleep(0.1)
        print(f"[DEBUG] result = {result[0]}")  # <- добавь это
        if time.time() - last_redraw[0] > 1:
            draw()
            last_redraw[0] = time.time()

    return result[0]

# --- Вспомогательные функции ---

def reboot_pi():
    show_message("Reboot...")
    time.sleep(1)
    clear()
    os.execv(sys.executable, [sys.executable] + sys.argv)


# --- Меню: Главное ---

@log_async
async def start_main_menu():
    selected_result = [None]

    def up_hold():
        selected_result[0] = "mac"

    def back_hold():
        reboot_pi()

    index = await run_menu(
        MAIN_MENU_ITEMS,
        visible_lines=VISIBLE_LINES,
        highlight_color="yellow",
        up_hold_action=up_hold,
        back_hold_action=back_hold
    )

    if selected_result[0]:
        return selected_result[0]
    if index is None:
        return None
    return MAIN_MENU_ITEMS[index].lower()


# --- Меню: Прошивка ---

@log_async
async def start_flash_menu():
    async def on_flash_selected(name):
        clear()
        await flash_firmware(name.lower())

    index = await run_menu(
        FLASH_ITEMS,
        visible_lines=VISIBLE_LINES,
        highlight_color="red",
        on_select=on_flash_selected
    )

    return "main" if index is "main" else "flash"


# --- Меню: Настройки (Принтер) ---

@log_async
async def start_settings_menu():
    async def on_toggle_printer(_):
        if printer_connection["connected"]:
            await disconnect_from_printer()
        else:
            await connect_to_printer()

    while True:
        label = f"Print: {'On' if printer_connection['connected'] else 'Off'}"
        index = await run_menu([label], visible_lines=1, on_select=on_toggle_printer)
        if index is None:
            return None
