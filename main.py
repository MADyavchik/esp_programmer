# main.py
import time
import traceback
import os
from menu_navigation import run_menu_loop

LOG_FILE = "/home/pauro/esp_programmer/error.log"  # можно изменить путь

def log_error(e):
    with open(LOG_FILE, "a") as f:
        f.write(f"\n--- ERROR at {time.ctime()} ---\n")
        traceback.print_exc(file=f)

def main():
    while True:
        try:
            run_menu_loop()
        except Exception as e:
            print("💥 Программа упала с ошибкой, перезапуск через 2 секунды")
            traceback.print_exc()
            log_error(e)
            time.sleep(2)  # немного подождём перед перезапуском

if __name__ == "__main__":
    main()
