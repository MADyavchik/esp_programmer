import os
import sys
import time
import asyncio

import state
from buttons import setup_buttons, safe_async
from oled_ui import draw_menu, clear, show_message
from utils import log_async
from esp_flasher import flash_firmware
from printer_functions import printer_connection, connect_to_printer, disconnect_from_printer
from print_config import DEFAULT_PRINTER_CONFIG

from system_status import update_activity

# --- Глобальные переменные ---

MAIN_MENU_ITEMS = ["FLASH", "UPDATE", "LOG", "SETTINGS"]
FLASH_ITEMS = ["TEST", "Universal", "Master", "Repeater", "Sens_SW", "Sens_OLD"]
SETTINGS_ITEMS = ["Print:", "Quant:"]
VISIBLE_LINES = 4


state.last_activity_time = [time.time()]



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
        update_activity()
        index = scroll[0] + cursor[0]
        item = items[index]
        if isinstance(item, dict) and item.get("label"):
            return  # Нельзя выбрать заголовок
        if on_select:
            await on_select(item)
        result[0] = index

    def up():
        update_activity()
        while True:
            if cursor[0] > 0:
                cursor[0] -= 1
            elif scroll[0] > 0:
                scroll[0] -= 1
            else:
                # Если на первом элементе, переход к последнему доступному
                max_index = len(items) - 1
                for i in reversed(range(len(items))):
                    if not (isinstance(items[i], dict) and items[i].get("label")):
                        scroll[0] = max(0, i - visible_lines + 1)
                        cursor[0] = i - scroll[0]
                        break
                break

            index = scroll[0] + cursor[0]
            if not (isinstance(items[index], dict) and items[index].get("label")):
                break

        draw()
        last_redraw[0] = time.time()

    def down():
        update_activity()
        while True:
            if cursor[0] < min(visible_lines - 1, len(items) - scroll[0] - 1):
                cursor[0] += 1
            elif scroll[0] + visible_lines < len(items):
                scroll[0] += 1
            else:
                # Если внизу — перейти к первому интерактивному
                for i in range(len(items)):
                    if not (isinstance(items[i], dict) and items[i].get("label")):
                        scroll[0] = 0
                        cursor[0] = i
                        break
                break

            index = scroll[0] + cursor[0]
            if not (isinstance(items[index], dict) and items[index].get("label")):
                break

        draw()
        last_redraw[0] = time.time()

    def back():
        update_activity()
        print("Back button pressed")  # Логирование нажатия кнопки "Назад"
        result[0] = "main"

    # Добавим обработчик зажатия кнопки "Вверх"
    def up_hold():
        update_activity()
        print("Up button held!")  # Логируем зажатие кнопки "Вверх"
        result[0] = "mac"

    # Задаем кнопки
    setup_buttons(up, down, back, lambda: safe_async(select),
                  up_hold_action=up_hold,
                  back_hold_action=back_hold_action)

    draw()

    while result[0] is None:
        await asyncio.sleep(0.1)

        if time.time() - last_redraw[0] > 1:
            #print("[DEBUG] redraw triggered")
            draw()
            last_redraw[0] = time.time()

    #print(f"[DEBUG] result = {result[0]}")  # <- добавь это
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
    def back_hold():
        reboot_pi()

    index = await run_menu(
        MAIN_MENU_ITEMS,
        visible_lines=VISIBLE_LINES,
        highlight_color="yellow",
        #up_hold_action=lambda: None,  # если хочешь добавить поведение — сделай это внутри run_menu
        back_hold_action=back_hold
    )

    # 🔍 Логика разруливания возвращаемого значения
    if isinstance(index, str):
        return index  # "main", "mac" и т.п.
    if isinstance(index, int):
        return MAIN_MENU_ITEMS[index].lower()
    return None


# --- Меню: Прошивка ---

@log_async
async def start_flash_menu():
    selected_result = None  # сюда сохраним результат прошивки (например, "log" или "flash")

    async def on_flash_selected(name):
        nonlocal selected_result
        clear()
        selected_result = await flash_firmware(name.lower())

    index = await run_menu(
        FLASH_ITEMS,
        visible_lines=VISIBLE_LINES,
        highlight_color="red",
        on_select=on_flash_selected
    )

    if index == "main":
        return "main"

    # Если прошивка вернула "log", то возвращаем его
    if selected_result is not None:
        return selected_result

    return "flash"


# --- Меню: Настройки (Принтер) ---

@log_async
async def start_settings_menu():
    while True:
        menu_items = [
            {"text": "Принтер", "label": True},
            {"text": f"Подкл: {'Да' if printer_connection['connected'] else 'Нет'}"},
            {"text": f"Копий: {DEFAULT_PRINTER_CONFIG.quantity}"},
            {"text": "Система", "label": True},
            {"text": f"Сон: {int(state.shutdown_timeout / 60)} мин"}
        ]

        index = await run_menu(menu_items, visible_lines=4, highlight_color="lime")

        if index == "main":
            return "main"

        if index == 1:
            # Переключение принтера
            #if printer_connection["connected"]:
                #await disconnect_from_printer()
            #else:
                #await connect_to_printer()
            return "print_connect"

        elif index == 2:
            # Изменение количества
            await change_print_quantity()

        elif index == 4:

            await change_shutdown_timeout()

async def change_print_quantity():
    options = [str(i) for i in range(1, 11)]
    idx = await run_menu(options, visible_lines=4, highlight_color="lime")

    if isinstance(idx, int):
        DEFAULT_PRINTER_CONFIG.quantity = int(options[idx])

async def change_shutdown_timeout():
    values = [1, 10, 30, 60]
    labels = [f"{v} мин" for v in values]

    idx = await run_menu(labels, visible_lines=4, highlight_color="white")
    if isinstance(idx, int):
        state.shutdown_timeout = values[idx] * 60
