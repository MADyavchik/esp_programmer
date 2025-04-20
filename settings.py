import os
import asyncio
import time
from oled_ui import show_message, clear, draw_main_menu
from buttons import setup_buttons
from printer_functions import get_device_by_mac, connect_printer, disconnect_printer
from utils import log_async
from print_config import DEFAULT_PRINTER_CONFIG

from buttons import safe_async  # Подключаем безопасный вызов async функций



printer_connection = {
    "mac": "01:EC:01:36:C3:86",
    "device": None,
    "printer": None,
    "connected": False,
}

# --- ПРИНТЕР ---
async def connect_to_printer(config=DEFAULT_PRINTER_CONFIG):
    device = await get_device_by_mac(printer_connection["mac"])
    if not device:
        show_message("Printer not found")
        await asyncio.sleep(1)
        return

    printer = await connect_printer(
        device,
        sticker_width=config.width,
        sticker_height=config.height,
        quantity=config.quantity,
        density=config.density
    )

    printer_connection["device"] = device
    printer_connection["printer"] = printer
    printer_connection["connected"] = True
    printer_connection["config"] = config  # <-- запомним
    show_message("Printer connected")
    await asyncio.sleep(1)

async def disconnect_from_printer():
    if printer_connection["printer"]:
        await disconnect_printer(printer_connection["printer"])
    printer_connection["device"] = None
    printer_connection["printer"] = None
    printer_connection["connected"] = False
    show_message("Printer disconnected")
    await asyncio.sleep(1)

# --- МЕНЮ ---
@log_async
async def start_settings_menu():
    await asyncio.sleep(0.1)
    menu_items = ["Print: ?"]
    selected = [0]
    selected_result = [None]
    last_redraw = [0]

    def refresh_labels():
        menu_items[0] = f"Print: {'Connected' if printer_connection['connected'] else 'Disconnected'}"

    def draw():
        refresh_labels()
        draw_main_menu(menu_items, selected[0], selected[0], visible_lines=1)

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

    setup_buttons(up, down, back, select)
    draw()

    while selected_result[0] is None:
        await asyncio.sleep(0.1)
        if time.time() - last_redraw[0] > 3:
            draw()
            last_redraw[0] = time.time()

    return selected_result[0]
