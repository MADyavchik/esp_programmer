# main.py
import time
import traceback
from menu_navigation import run_menu_loop
from oled_ui import clear
import os

from system_status import status_updater
import threading

def log_error(e):
    with open("error.log", "a") as f:
        f.write(f"{time.ctime()}: {repr(e)}\n")
        traceback.print_exc(file=f)

def start_status_thread():
    t = threading.Thread(target=status_updater, daemon=True)
    t.start()

def main():
    start_status_thread()
    while True:
        try:
            if os.path.exists("exit.flag"):
                print("🔚 Обнаружен флаг выхода.")
                os.remove("exit.flag")
                break

            run_menu_loop()
        except KeyboardInterrupt:
            print("⏹ Выход по Ctrl+C")
            clear()
            break
        except Exception as e:
            print("💥 Программа упала с ошибкой, перезапуск через 2 секунды")
            traceback.print_exc()
            log_error(e)
            time.sleep(2)

if __name__ == "__main__":
    main()
