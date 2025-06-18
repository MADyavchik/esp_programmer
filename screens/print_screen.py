# screens/print_screen.py
import asyncio
from oled_ui import show_message, clear
from printer_functions import print_mac_address, printer_connection, disconnect_from_printer, connect_to_printer
from utils import log_async
import state
from oled_ui import animate_activity


@log_async
async def run_print_screen():
    clear()
    show_message("Печать MAC...")
    await asyncio.sleep(0.5)

    mac_address = state.mac_address

    if printer_connection["connected"] and printer_connection.get("printer"):
        try:
            # ▶️ Запуск анимации печати
            stop_event = asyncio.Event()
            animation_task = asyncio.create_task(animate_activity(stop_event, message="Печать..."))

            # 🖨️ Печать MAC-адреса
            await print_mac_address(
                printer_connection["printer"],
                mac_address,
                config=printer_connection["config"]
            )

            # ⏹️ Остановка анимации
            stop_event.set()
            await animation_task

            # ✅ Сообщение об успехе
            clear()
            show_message("MAC напечатан")

        except Exception as e:
            clear()
            show_message("Ошибка печати")
            print(f"Ошибка печати: {e}")
    else:
        clear()
        show_message("Принтер не подключен")

    await asyncio.sleep(2)
    return "log"
@log_async
async def run_print_connect():
    clear()
    # Переключение принтера
    if printer_connection["connected"]:
        await disconnect_from_printer()
    else:
        show_message("Подключение...")
        await connect_to_printer()

    return "settings"
