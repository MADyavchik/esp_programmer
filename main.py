# main.py
import time
import traceback
from menu_navigation import run_menu_loop
from oled_ui import clear

def log_error(e):
    with open("error.log", "a") as f:
        f.write(f"{time.ctime()}: {repr(e)}\n")
        traceback.print_exc(file=f)

def main():
    while True:
        try:
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
