# git_update.py
import subprocess
import time
import os
import sys
from oled_ui import draw_progress_bar, show_message, clear
from buttons import btn_back
from buttons import setup_buttons

def reboot():
    os.system("sudo reboot")

# Главная функция обновления
def update_repo():
    try:
        show_message("Updating...")
        print("[GIT] Выполняю git pull...")
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        time.sleep(1)

        if result.returncode == 0:
            show_message("Success!")
            print("[GIT] Репозиторий успешно обновлен!")
            time.sleep(2)

            show_message("Rebooting app...")
            time.sleep(1)

            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            show_message(f"Err: {result.stderr}")
            print(f"[GIT] Ошибка при обновлении: {result.stderr}")
            time.sleep(2)

    except Exception as e:
        show_message(f"Err: {e}")
        print(f"[GIT] Ошибка: {e}")

# Обёртка для вызова из меню
def start_git_update():
    clear()
    setup_buttons(None, None, None, None)
    update_repo()

    # Ждём нажатия кнопки Назад
    while not btn_back.is_pressed:
        time.sleep(0.1)
    while btn_back.is_pressed:
        time.sleep(0.1)

    return "main"
