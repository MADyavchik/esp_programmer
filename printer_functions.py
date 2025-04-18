import sys
import os

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
    # Создаем белое изображение
    width, height = 384, 100  # Ширина зависит от модели принтера
    image = Image.new("1", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Шрифт: можно заменить на кастомный путь, если нужно
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except:
        font = ImageFont.load_default()

    # Текст
    text = f"MAC Address:\n{mac_address}"
    draw.multiline_text((10, 10), text, font=font, fill=0)

    # Отправка изображения в принтер
    await printer.print_image(image)

# Пример функции для отключения принтера
async def disconnect_printer(printer):
    await printer.disconnect()
    print("Printer disconnected")
