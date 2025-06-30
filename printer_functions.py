#printer_functions.py
import sys
import os
import struct
from types import MethodType

import state
from oled_ui import animate_activity

sys.path.append(os.path.abspath('/home/pauro/NiimPrintX'))

import asyncio
from NiimPrintX.nimmy.printer import PrinterClient, RequestCodeEnum
from bleak import BleakScanner
from PIL import Image, ImageDraw, ImageFont
from oled_ui import show_message


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
    quantity = config.quantity
    density = config.density

    label_text = state.firmware_version
    padding = 4

    image = Image.new("1", (width, height), "white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 28)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    max_line_length = 9
    cleaned = ''.join([c for i, c in enumerate(mac_address) if (i + 1) % max_line_length != 0])
    lines = [cleaned[i:i + (max_line_length - 1)] for i in range(0, len(cleaned), max_line_length - 1)]

    text_height = sum([draw.textbbox((0, 0), line, font=font)[3] for line in lines])
    x = (width - max([draw.textbbox((0, 0), line, font=font)[2] for line in lines])) // 2
    y = (height - text_height) // 2



    y_offset = y
    for line in lines:
        draw.text((x, y_offset), line, font=font, fill=0)
        y_offset += draw.textbbox((0, 0), line, font=font)[3]

    # Подпись с версией

    text_bbox = draw.textbbox((0, 0), label_text, font=small_font)
    #text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    draw.text(
        (x, height - text_height - padding),  # нижний левый угол
        label_text,
        font=small_font,
        fill=0  # чёрный для печати
    )

    image = image.rotate(270, expand=True)

    # 👇 Добавляем анимацию во время печати
    #stop_event = asyncio.Event()
    #animation_task = asyncio.create_task(animate_activity(stop_event, message="Печать..."))

    try:
        await printer.print_image(image, quantity=quantity, density=density)

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

    except Exception as e:
        print(f"Ошибка: {e}")
    #finally:
        # ✅ Остановить анимацию в любом случае
        #stop_event.set()
        #await animation_task


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


async def monitor_printer_connection(interval=10):
    while True:
        printer = printer_connection.get("printer")
        if not printer:
            break

        try:
            if hasattr(printer, "get_print_status"):
                status = await printer.get_print_status()
                if not status or status.get("error", False):
                    raise Exception("Printer not responding")
            else:
                raise Exception("get_print_status not supported")
        except Exception as e:
            print(f"⚠️ Принтер отключён: {e}")
            printer_connection.update({
                "connected": False,
                "printer": None,
                "device": None,
            })
            show_message("Printer disconnected")
            break

        await asyncio.sleep(interval)


async def disconnect_from_printer():
    global monitoring_task

    if printer_connection["printer"]:
        await disconnect_printer(printer_connection["printer"])

    printer_connection.update({
        "device": None,
        "printer": None,
        "connected": False,
    })
    show_message("Printer disconnected")
    await asyncio.sleep(1)

    if monitoring_task and not monitoring_task.done():
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass

async def connect_to_printer(config=DEFAULT_PRINTER_CONFIG):
    global monitoring_task

    device = await get_device_by_mac(printer_connection["mac"])
    if not device:
        #show_message("Printer not found")
        #await asyncio.sleep(1)
        return "Принтер не найден"

    printer = await connect_printer(device)

    printer_connection.update({
        "device": device,
        "printer": printer,
        "connected": True,
        "config": config,
    })
    #show_message("Printer connected")
    #await asyncio.sleep(1)
    return "Принтер подключен"


printer_connection = {
    "mac": "01:EC:01:36:C3:86",
    "device": None,
    "printer": None,
    "connected": False,
}
monitoring_task = None
