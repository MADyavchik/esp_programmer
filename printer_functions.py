import sys
import os
import struct
from types import MethodType

sys.path.append(os.path.abspath('/home/pauro/NiimPrintX'))

import asyncio
from NiimPrintX.nimmy.printer import PrinterClient, RequestCodeEnum
from bleak import BleakScanner
from PIL import Image, ImageDraw, ImageFont

# Указываем путь к библиотеке NiimPrintX


# Поиск устройства по MAC
async def get_device_by_mac(mac_address):
    devices = await BleakScanner.discover()
    for device in devices:
        if device.address == mac_address:
            return device
    return None

# Подключение к принтеру
async def connect_printer(device):
    printer = PrinterClient(device)
    await printer.connect()
    return printer

# Печать текста (например, MAC-адреса)
async def print_mac_address(printer, mac_address: str):
    # Monkey patch get_print_status
    async def patched_get_print_status(self):
        packet = await self._transport.read()
        if len(packet.data) < 4:
            return (0, 0, 0)
        page, progress1, progress2 = struct.unpack(">HBB", packet.data)
        return (page, progress1, progress2)

    printer.get_print_status = MethodType(patched_get_print_status, printer)

    # Генерация изображения
    width, height = 384, 100
    image = Image.new("1", (width, height), "white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except:
        font = ImageFont.load_default()

    text = f"{mac_address}"
    draw.multiline_text((10, 10), text, font=font, fill=0)

    # Повернуть изображение на 90 градусов по часовой стрелке
    image = image.rotate(270, expand=True)

    # Печать
    await printer.print_image(image)

# Пример функции для отключения принтера
async def disconnect_printer(printer):
    await printer.disconnect()
    print("Printer disconnected")
