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

    # Monkey patch для безопасного получения статуса печати
    async def safe_get_print_status(self):
        packet = await self.send_command(RequestCodeEnum.GET_PRINT_STATUS, b"")
        if not packet or not hasattr(packet, "data") or len(packet.data) < 4:
            return None  # Возвращаем None, если данные отсутствуют или некорректны
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
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except:
        font = ImageFont.load_default()

    # Текст, который нужно нарисовать
    text = f"{mac_address}"

    # Разбиваем текст на строки, например, каждая строка по 9 символов
    max_line_length = 9  # Максимальная длина строки
    lines = [text[i:i+max_line_length] for i in range(0, len(text), max_line_length)]

    # Вычисляем высоту текста (с учетом нескольких строк)
    text_height = 0
    for line in lines:
        _, line_height = draw.textbbox((0, 0), line, font=font)[2:4]
        text_height += line_height

    # Вычисляем координаты для центрирования текста
    x = (width - max([draw.textbbox((0, 0), line, font=font)[2] for line in lines])) // 2
    y = (height - text_height) // 2

    # Рисуем каждую строку на изображении
    y_offset = y
    for line in lines:
        draw.text((x, y_offset), line, font=font, fill=0)
        _, line_height = draw.textbbox((0, 0), line, font=font)[2:4]
        y_offset += line_height

    # Повернуть изображение на 90 градусов по часовой стрелке
    image = image.rotate(270, expand=True)

    # Печать с дополнительной проверкой на None
    status = await printer.print_image(image)
    if status is None:
        print("Ошибка: статус печати не получен или неверный.")
    else:
        try:
            if 'page' in status and status['page'] == status.get('quantity', 0):
                print("Изображение успешно отправлено на печать.")
            else:
                print("Не удалось получить корректный статус печати.")
        except Exception as e:
            print(f"Ошибка при обработке статуса печати: {e}")

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
