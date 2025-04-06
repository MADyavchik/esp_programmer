import subprocess
import os
import sys
from menu import draw_menu  # Импортируем функцию для рисования меню

# Функция для обновления репозитория
def update_repo():
    try:
        # Начало обновления
        draw_menu()  # Показываем начальное сообщение на экране
        with canvas(device) as draw:
            draw.text((10, 10), "Обновление началось...", font=font, fill="white")

        print("[GIT] Выполняю git pull...")
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)

        if result.returncode == 0:
            # Обновление прошло успешно
            with canvas(device) as draw:
                draw.text((10, 10), "Репозиторий обновлён!", font=font, fill="white")
            print("[GIT] Репозиторий успешно обновлен!")

            # Перезапуск программы после успешного обновления
            print("[GIT] Перезапуск программы...")
            os.execv(sys.executable, ['python3'] + sys.argv)  # Перезапуск текущего скрипта (main.py)
        else:
            # Ошибка при обновлении
            with canvas(device) as draw:
                draw.text((10, 10), f"Ошибка: {result.stderr}", font=font, fill="white")
            print(f"[GIT] Ошибка при обновлении: {result.stderr}")

    except Exception as e:
        # Общая ошибка
        with canvas(device) as draw:
            draw.text((10, 10), f"Ошибка: {e}", font=font, fill="white")
        print(f"[GIT] Ошибка: {e}")
