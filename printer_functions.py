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

    # Monkey patch для безопасного получения статуса печати
    async def safe_get_print_status(self):
        packet = await self.send_command(RequestCodeEnum.GET_PRINT_STATUS, b"")
        if not packet or not hasattr(packet, "data") or len(packet.data) < 4:
            return None
        return struct.unpack(">HBB", packet.data)

    # Подставляем наш патч
    printer.get_print_status = MethodType(safe_get_print_status, printer)

    return printer

# Печать текста (например, MAC-адреса)
async def print_mac_address(printer, mac_address: str):
    # Генерация изображения
    width, height = 175, 120
    image = Image.new("1", (width, height), "white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except:
        font = ImageFont.load_default()

    # Текст, который нужно нарисовать
    text = f"{mac_address}"

    # Получаем размеры текста
    text_width, text_height = draw.textsize(text, font=font)

    # Вычисляем координаты для центрирования текста
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Рисуем текст по вычисленным координатам
    draw.text((x, y), text, font=font, fill=0)

    # Повернуть изображение на 90 градусов по часовой стрелке
    image = image.rotate(270, expand=True)

    # Печать
    await printer.print_image(image)

# Пример функции для отключения принтера
async def disconnect_printer(printer):
    await printer.disconnect()
    print("Printer disconnected")

# Пример использования
async def main():
    mac = "01:EC:01:36:C3:86"  # Пример MAC-адреса
    device = await get_device_by_mac(mac)

    if device:
        print(f"Устройство найдено: {device.name} ({device.address})")
        printer = await connect_printer(device)  # Подключаемся к принтеру
        await print_mac_address(printer, mac)   # Печатаем MAC-адрес
        await disconnect_printer(printer)       # Отключаем принтер
    else:
        print("Устройство не найдено.")

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
