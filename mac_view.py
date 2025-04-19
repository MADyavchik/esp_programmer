import time
import asyncio
from utils import log_async
from oled_ui import draw_mac_address, clear
from esp_flasher import get_mac_address
from buttons import btn_back
from printer_functions import connect_printer, print_mac_address, disconnect_printer, get_device_by_mac

@log_async
async def show_mac_address():
    clear()
    mac = get_mac_address()
    draw_mac_address(mac)

    async def print_mac():
        device = await get_device_by_mac("01:EC:01:36:C3:86")
        if device:
            print(f"Устройство найдено: {device.name} ({device.address})")
            printer = await connect_printer(device)
            await print_mac_address(printer, mac)
            await disconnect_printer(printer)

    from buttons import safe_async
    safe_async(print_mac)

    while not btn_back.is_pressed:
        await asyncio.sleep(0.1)
    while btn_back.is_pressed:
        await asyncio.sleep(0.1)

    return "main"
