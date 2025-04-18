import os
import asyncio
import time
from oled_ui import show_message, clear, draw_main_menu
from buttons import setup_buttons
from printer_functions import get_device_by_mac, connect_printer, disconnect_printer

printer_connection = {
    "mac": "01:EC:01:36:C3:86",
    "device": None,
    "printer": None,
    "connected": False,
}

def toggle_wifi():
    os.system("nmcli radio wifi off" if is_wifi_enabled() else "nmcli radio wifi on")

def toggle_bluetooth():
    os.system("rfkill block bluetooth" if is_bt_enabled() else "rfkill unblock bluetooth")

def is_wifi_enabled():
    result = os.popen("nmcli radio wifi").read().strip()
    return result == "enabled"

def is_bt_enabled():
    result = os.popen("rfkill list bluetooth").read()
    return "Soft blocked: yes" not in result

async def connect_to_printer():
    device = await get_device_by_mac(printer_connection["mac"])
    if not device:
        show_message("Printer not found")
        await asyncio.sleep(1)
        return
    printer = await connect_printer(device)
    printer_connection["device"] = device
    printer_connection["printer"] = printer
    printer_connection["connected"] = True
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

async def start_settings_menu():
    menu_items = ["Wi-Fi: ?", "Bluetooth: ?", "Print: ?"]
    selected = [0]
    selected_result = [None]
    last_redraw = [0]

    def refresh_labels():
        menu_items[0] = f"Wi-Fi: {'ON' if is_wifi_enabled() else 'OFF'}"
        menu_items[1] = f"Bluetooth: {'ON' if is_bt_enabled() else 'OFF'}"
        menu_items[2] = f"Print: {'Connected' if printer_connection['connected'] else 'Disconnected'}"

    def draw():
        refresh_labels()
        draw_main_menu(menu_items, selected[0], selected[0], visible_lines=2)

    async def select():
        if selected[0] == 0:
            toggle_wifi()
        elif selected[0] == 1:
            toggle_bluetooth()
        elif selected[0] == 2:
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

    # Подключаем асинхронные версии кнопок
    setup_buttons(up, down, back, lambda: asyncio.create_task(select()))

    draw()
    while selected_result[0] is None:
        await asyncio.sleep(0.1)
        if time.time() - last_redraw[0] > 3:
            draw()
            last_redraw[0] = time.time()

    return selected_result[0]
