import subprocess
import os
import sys
from menu import display_status  # Импортируем функцию для отображения статуса

# Функция для обновления репозитория
def update_repo():
    try:
        # Начало обновления
        display_status("Обновление началось...")  # Отображаем статус на экране

        print("[GIT] Выполняю git pull...")
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)

        if result.returncode == 0:
            # Обновление прошло успешно
            display_status("Репозиторий обновлён!")  # Отображаем успешное обновление
            print("[GIT] Репозиторий успешно обновлен!")

            # Перезапуск программы после успешного обновления
            print("[GIT] Перезапуск программы...")
            os.execv(sys.executable, ['python3'] + sys.argv)  # Перезапуск текущего скрипта (main.py)
        else:
            # Ошибка при обновлении
            display_status(f"Ошибка: {result.stderr}")  # Отображаем ошибку на экране
            print(f"[GIT] Ошибка при обновлении: {result.stderr}")

    except Exception as e:
        # Общая ошибка
        display_status(f"Ошибка: {e}")  # Отображаем ошибку на экране
        print(f"[GIT] Ошибка: {e}")
