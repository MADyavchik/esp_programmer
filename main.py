#main.py
import time
import traceback
import os
import asyncio
import threading
import loop_reference

from menu_navigation import run_menu_loop
from oled_ui import clear
from system_status import status_updater
from utils import log_error  # ✅ теперь используем версию из utils

main_loop = None


def start_status_thread():
    t = threading.Thread(target=status_updater, daemon=True)
    t.start()

async def main():

    loop_reference.main_loop = asyncio.get_running_loop()

    start_status_thread()
    while True:
        try:
            if os.path.exists("exit.flag"):
                print("🔚 Обнаружен флаг выхода.")
                os.remove("exit.flag")
                break

            await run_menu_loop()
        except KeyboardInterrupt:
            print("⏹ Выход по Ctrl+C")
            clear()
            break
        except Exception as e:
            print("💥 Программа упала с ошибкой, перезапуск через 2 секунды")
            traceback.print_exc()
            log_error(e)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
