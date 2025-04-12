# git_update.py
import subprocess
import time
import os
import sys
def reboot(): os.system("sudo reboot")
# init display
from oled_ui import draw_progress_bar, show_message, clear
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont

# Настройка дисплея
#serial = i2c(port=1, address=0x3C)
#device = ssd1306(serial)

# Подгружаем шрифт
#try:
    #font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
#except:
    #font = ImageFont.load_default()

# Функция для обновления репозитория
def update_repo():
    try:
        # Начало обновления

        show_message("Updating...")
        print("[GIT] Выполняю git pull...")
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        time.sleep(1)

        if result.returncode == 0:
            # Обновление прошло успешно
            show_message("Success!")
            print("[GIT] Репозиторий успешно обновлен!")
            time.sleep(2)

            # Перезапуск программы после успешного обновления
            #reboot()
            show_message("Rebooting app...")

            time.sleep(1)

            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            # Ошибка при обновлении
            show_message(f"Err: {result.stderr}")
            print(f"[GIT] Ошибка при обновлении: {result.stderr}")
            time.sleep(2)

    except Exception as e:
        # Общая ошибка
        show_message(f"Err: {e}")

        print(f"[GIT] Ошибка: {e}")
