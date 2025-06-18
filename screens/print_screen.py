# screens/print_screen.py
import asyncio
from oled_ui import show_message, clear
from printer_functions import print_mac_address, printer_connection
from utils import log_async
import state


@log_async
async def run_print_screen():
    clear()
    show_message("Печать MAC...")
    await asyncio.sleep(0.5)  # небольшая пауза перед началом

    mac_address = state.mac_address

    if printer_connection["connected"] and printer_connection.get("printer"):
        try:
            await print_mac_address(
                printer_connection["printer"],
                mac_address,
                config=printer_connection["config"]
            )
            clear()
            show_message("✅ MAC напечатан")
        except Exception as e:
            clear()
            show_message("❌ Ошибка печати")
            print(f"Ошибка печати: {e}")
    else:
        clear()
        show_message("⚠️ Принтер не подключен")

    await asyncio.sleep(2)  # Показать результат пару секунд
