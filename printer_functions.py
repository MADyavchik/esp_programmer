import sys
import os
import struct
from types import MethodType

sys.path.append(os.path.abspath('/home/pauro/NiimPrintX'))

import asyncio
from NiimPrintX.nimmy.printer import PrinterClient, RequestCodeEnum
from bleak import BleakScanner
from PIL import Image, ImageDraw, ImageFont


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

    # Патч для безопасного получения статуса печати
    async def safe_get_print_status(self):
        packet = await self.send_command(RequestCodeEnum.GET_PRINT_STATUS, b"")
        if not packet or not hasattr(packet, "data") or len(packet.data) < 4:
            return {
                'page': 0,
                'quantity': 0,
                'error': True,
                'raw': packet.data if packet else b''
            }
        try:
            pages_printed, val1, val2 = struct.unpack(">HBB", packet.data)
            return {
                'page': pages_printed,
                'quantity': 1,
                'error': False,
                'raw': packet.data
            }
        except Exception as e:
            return {
                'page': 0,
                'quantity': 0,
                'error': True,
                'raw': packet.data,
                'exception': str(e)
            }

    # Подставляем наш патч
    printer.get_print_status = MethodType(safe_get_print_status, printer)

    return printer

# Печать текста (например, MAC-адреса)
from print_config import DEFAULT_PRINTER_CONFIG

async def print_mac_address(printer, mac_address: str, config=DEFAULT_PRINTER_CONFIG):
    width = config.width
    height = config.height
    quantity = config.quantity  # Количество копий
    density = config.density    # Плотность

    image = Image.new("1", (width, height), "white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()

    max_line_length = 9
    lines = [mac_address[i:i + max_line_length] for i in range(0, len(mac_address), max_line_length)]

    text_height = sum([draw.textbbox((0, 0), line, font=font)[3] for line in lines])
    x = (width - max([draw.textbbox((0, 0), line, font=font)[2] for line in lines])) // 2
    y = (height - text_height) // 2

    y_offset = y
    for line in lines:
        draw.text((x, y_offset), line, font=font, fill=0)
        y_offset += draw.textbbox((0, 0), line, font=font)[3]

    image = image.rotate(270, expand=True)

    await printer.print_image(image, sticker_width=width, sticker_height=height, quantity=quantity, density=density)

    # Явно запрашиваем статус
    if hasattr(printer, "get_print_status"):
        status = await printer.get_print_status()
    else:
        print("⚠️ Принтер не поддерживает получение статуса.")
        return

    if not isinstance(status, dict) or status.get("error", False):
        print(f"❌ Ошибка: статус печати не получен или содержит ошибку. Статус: {status}")
        return

    printed = status.get("page", 0)
    expected = status.get("quantity", 1)

    if printed >= expected:
        print("✅ Изображение успешно отправлено на печать.")
    else:
        print(f"⚠️ Печать завершена не полностью. Статус: {status}")

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
