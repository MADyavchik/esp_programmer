import sys
import os
import asyncio
from NiimPrintX.nimmy.printer import PrinterClient, RequestCodeEnum
from bleak import BleakScanner

# Указываем путь к библиотеке NiimPrintX
sys.path.append(os.path.abspath('/path/to/NiimPrintX'))

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
async def print_mac_address(printer, mac_address):
    # Отправка команды на печать текста
    await printer.print_text(f"MAC Address: {mac_address}")
    print(f"Printed MAC address: {mac_address}")

# Пример функции для отключения принтера
async def disconnect_printer(printer):
    await printer.disconnect()
    print("Printer disconnected")
